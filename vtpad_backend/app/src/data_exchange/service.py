"""Safe, versioned JSON/CSV exchange for space-scoped suites and test cases.

CSV v1 starts with #vtpad-data-exchange:v1:<base64url JSON metadata>.
The following table has one suite, section or case row per record. Sections
use stable keys and parent keys; section_path is descriptive. Custom-field
columns are custom_field:<stable_key> and cells contain JSON values.
"""

from __future__ import annotations

import base64
import csv
import hashlib
import html
import io
import json
import re
import uuid
from typing import Any, Literal

from fastapi import HTTPException
from tortoise.exceptions import IntegrityError
from tortoise.transactions import in_transaction

from ..common.crypto import user_payload
from ..common.right_guard import check_user_into_space
from ..custom_field.model import CustomFieldEntityType, CustomFieldModel, CustomFieldType, CustomFieldValueModel
from ..custom_field.service import validate_value
from ..section.model import SectionModel
from ..space.model import SpaceModel
from ..test_case.model import TestCaseModel, TestCasePriority, TestCaseStatus, TestCaseType
from ..test_case.service import TestCaseService
from ..test_suite.model import TestSuiteModel
from .model import ImportReceiptModel

Format = Literal["json", "csv"]
MAX_BYTES = 5 * 1024 * 1024
MAX_ROWS = 10_000
MAX_CASES = 5_000
MAX_DEPTH = 20
_CASE_TYPES = {item.value for item in TestCaseType}
_PRIORITIES = {item.value for item in TestCasePriority}
_CSV_COLUMNS = [
    "record_type", "suite_key", "suite_name", "suite_description",
    "section_key", "parent_section_key", "section_name", "section_description",
    "section_path", "case_key", "title", "short_name", "type", "priority",
    "text", "steps", "expected_results", "preconditions", "postconditions",
    "estimated_duration_seconds", "tags",
]


def _bad(detail: str) -> HTTPException:
    return HTTPException(status_code=422, detail=detail)


def _actor_id(request) -> uuid.UUID:
    value = getattr(getattr(request, "state", None), "mcp_authenticated_user_id", None)
    if value is None:
        authorization = request.headers.get("authorization", "")
        parts = authorization.split(" ", 1)
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise HTTPException(status_code=401, detail="not auth")
        value = user_payload(parts[1]).get("id")
    try:
        return uuid.UUID(str(value))
    except (ValueError, TypeError, AttributeError) as exc:
        raise HTTPException(status_code=401, detail="not auth") from exc


async def _authorize(
    space_id: str | uuid.UUID,
    request,
    *,
    write_capabilities: tuple[str, ...] = (),
) -> uuid.UUID:
    try:
        space_uuid = uuid.UUID(str(space_id))
    except (ValueError, TypeError, AttributeError) as exc:
        raise HTTPException(status_code=404, detail="Space not found") from exc
    await check_user_into_space(str(space_uuid), request)
    actor_id = _actor_id(request)
    if write_capabilities:
        from ..common.space_capabilities import require_space_capability
        for capability in write_capabilities:
            await require_space_capability(str(actor_id), str(space_uuid), capability)
    return actor_id


def _check_format(fmt: str) -> Format:
    if fmt not in ("json", "csv"):
        raise HTTPException(status_code=415, detail="format must be json or csv")
    return fmt  # type: ignore[return-value]


def _bounded_content(content: bytes) -> None:
    if not isinstance(content, (bytes, bytearray)):
        raise _bad("Import content must be bytes")
    if len(content) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="Import content exceeds the 5 MiB limit")


def _json_depth(value: Any, depth: int = 0) -> None:
    if depth > MAX_DEPTH + 8:
        raise _bad("Import document is nested too deeply")
    if isinstance(value, dict):
        for item in value.values():
            _json_depth(item, depth + 1)
    elif isinstance(value, list):
        for item in value:
            _json_depth(item, depth + 1)


def _unique_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON object key")
        result[key] = value
    return result


def _string(value: Any, label: str, *, required: bool = False, max_length: int | None = None) -> str | None:
    if value is None and not required:
        return None
    if not isinstance(value, str) or (required and not value.strip()):
        raise _bad(f"{label} must be a non-empty string")
    if max_length is not None and len(value) > max_length:
        raise _bad(f"{label} exceeds its maximum length")
    return value


def _stable_key(value: Any, label: str) -> str:
    result = _string(value, label, required=True, max_length=100)
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]*", result or ""):
        raise _bad(f"{label} has an invalid format")
    return result  # type: ignore[return-value]


def _normalize_cases(raw_cases: Any, counts: dict[str, Any]) -> list[dict]:
    if not isinstance(raw_cases, list):
        raise _bad("cases must be a list")
    result = []
    for raw in raw_cases:
        if not isinstance(raw, dict):
            raise _bad("case rows must be objects")
        key = _stable_key(raw.get("stable_key"), "case stable_key")
        if key in counts["case_keys"]:
            raise _bad("case stable_key values must be unique")
        counts["case_keys"].add(key)
        counts["cases"] += 1
        if counts["cases"] > MAX_CASES:
            raise _bad("Import contains more than 5,000 cases")
        case = {
            "stable_key": key,
            "title": _string(raw.get("title"), "case title", required=True),
            "short_name": (_string(raw.get("short_name"), "case short_name", max_length=255) or "").strip() or None,
            "type": raw.get("type", "manual"),
            "priority": raw.get("priority", "P2"),
            "text": _string(raw.get("text"), "case text"),
            "steps": _string(raw.get("steps"), "case steps"),
            "expected_results": _string(raw.get("expected_results"), "case expected_results"),
            "preconditions": _string(raw.get("preconditions"), "case preconditions"),
            "postconditions": _string(raw.get("postconditions"), "case postconditions"),
            "estimated_duration_seconds": raw.get("estimated_duration_seconds"),
            "tags": raw.get("tags", []),
            "custom_fields": raw.get("custom_fields", {}),
        }
        if case["type"] not in _CASE_TYPES or case["priority"] not in _PRIORITIES:
            raise _bad("case type or priority is invalid")
        duration = case["estimated_duration_seconds"]
        if duration is not None and (isinstance(duration, bool) or not isinstance(duration, int) or duration < 0):
            raise _bad("estimated_duration_seconds must be a non-negative integer")
        if not isinstance(case["tags"], list) or any(not isinstance(t, str) for t in case["tags"]):
            raise _bad("case tags must be a list of strings")
        case["tags"] = TestCaseService._normalize_tags(case["tags"])
        if not isinstance(case["custom_fields"], dict):
            raise _bad("case custom_fields must be an object keyed by field stable_key")
        result.append(case)
    return result


def _walk_json_sections(sections: Any, parent: str | None, depth: int, counts: dict[str, Any]) -> list[dict]:
    if not isinstance(sections, list):
        raise _bad("sections must be a list")
    if depth > MAX_DEPTH and sections:
        raise _bad("Import contains more than 20 section levels")
    result = []
    for raw in sections:
        if not isinstance(raw, dict):
            raise _bad("section rows must be objects")
        key = _stable_key(raw.get("stable_key"), "section stable_key")
        if key in counts["section_keys"]:
            raise _bad("section stable_key values must be unique")
        counts["section_keys"].add(key)
        result.append({
            "stable_key": key,
            "name": _string(raw.get("name"), "section name", required=True, max_length=500),
            "description": _string(raw.get("description"), "section description"),
            "parent_key": parent,
            "depth": depth,
            "cases": _normalize_cases(raw.get("cases", []), counts),
            "children": _walk_json_sections(raw.get("sections", []), key, depth + 1, counts),
        })
    return result


def _flatten(suites: list[dict]) -> dict[str, list[dict]]:
    sections: list[dict] = []
    cases: list[dict] = []
    def add_cases(items, suite, section=None):
        for source in items:
            case = dict(source)
            case["suite_key"] = suite["stable_key"]
            case["section_key"] = section["stable_key"] if section else None
            cases.append(case)
    def add_sections(items, suite):
        for section in items:
            sections.append(section)
            add_cases(section["cases"], suite, section)
            add_sections(section["children"], suite)
    for suite in suites:
        add_cases(suite["cases"], suite)
        add_sections(suite["sections"], suite)
    return {"sections": sections, "cases": cases}


def _normalize_fields(raw_fields: Any) -> list[dict]:
    if not isinstance(raw_fields, list):
        raise _bad("custom_fields definitions must be a list")
    result, keys = [], set()
    for raw in raw_fields:
        if not isinstance(raw, dict):
            raise _bad("custom-field definitions must be objects")
        key = _stable_key(raw.get("stable_key"), "custom-field stable_key")
        if key in keys:
            raise _bad("custom-field stable_key values must be unique")
        keys.add(key)
        field_type = raw.get("field_type")
        if field_type not in {item.value for item in CustomFieldType}:
            raise _bad("custom-field type is invalid")
        options = raw.get("options", [])
        if not isinstance(options, list) or any(not isinstance(item, str) or not item.strip() for item in options):
            raise _bad("custom-field options must be non-empty strings")
        if field_type in ("select", "multiselect"):
            if not options or len(set(options)) != len(options):
                raise _bad("select custom fields require unique options")
        elif options:
            raise _bad("only select custom fields may define options")
        name = _string(raw.get("name"), "custom-field name", required=True, max_length=500)
        required = raw.get("required", False)
        if not isinstance(required, bool):
            raise _bad("custom-field required must be boolean")
        result.append({"stable_key": key, "name": name, "field_type": field_type,
                       "options": options, "required": required})
    return result


def _normalize_json(content: bytes) -> dict:
    try:
        document = json.loads(content.decode("utf-8"), object_pairs_hook=_unique_json_object)
    except (UnicodeDecodeError, json.JSONDecodeError, RecursionError, ValueError) as exc:
        raise _bad("Import must be valid UTF-8 JSON") from exc
    _json_depth(document)
    if not isinstance(document, dict) or type(document.get("schema_version")) is not int or document.get("schema_version") != 1:
        raise _bad("JSON schema_version must be 1")
    raw_suites = document.get("suites")
    if not isinstance(raw_suites, list):
        raise _bad("suites must be a list")
    counts = {"cases": 0, "section_keys": set(), "case_keys": set()}
    suites, suite_keys = [], set()
    for raw in raw_suites:
        if not isinstance(raw, dict):
            raise _bad("suite rows must be objects")
        key = _stable_key(raw.get("stable_key"), "suite stable_key")
        if key in suite_keys:
            raise _bad("suite stable_key values must be unique")
        suite_keys.add(key)
        suites.append({
            "stable_key": key,
            "name": _string(raw.get("name"), "suite name", required=True, max_length=500),
            "description": _string(raw.get("description"), "suite description"),
            "cases": _normalize_cases(raw.get("cases", []), counts),
            "sections": _walk_json_sections(raw.get("sections", []), None, 1, counts),
        })
    unassigned_cases = _normalize_cases(document.get("unassigned_cases", []), counts)
    if len(suites) + len(counts["section_keys"]) + counts["cases"] > MAX_ROWS:
        raise _bad("Import contains more than 10,000 rows")
    definitions = _normalize_fields(document.get("custom_fields", []))
    field_keys = {item["stable_key"] for item in definitions}
    for case in [*_flatten(suites)["cases"], *unassigned_cases]:
        if set(case["custom_fields"]) - field_keys:
            raise _bad("case references an unknown custom-field stable_key")
    return {"schema_version": 1, "custom_fields": definitions, "suites": suites,
            "unassigned_cases": unassigned_cases}


def _field_like(definition: dict):
    return type("ImportField", (), {"field_type": definition["field_type"], "options": definition["options"],
                                    "required": definition["required"], "name": definition["name"]})()


def _csv_cell_value(cell: str, field: dict) -> Any:
    if cell == "":
        return None
    try:
        value = json.loads(cell)
    except json.JSONDecodeError as exc:
        raise _bad("CSV custom-field cells must contain JSON values") from exc
    if field["field_type"] == "text" and not isinstance(value, str):
        raise _bad("CSV text custom-field cells must contain JSON strings")
    return value


def _normalize_csv(content: bytes) -> dict:
    try:
        source = content.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise _bad("CSV must be valid UTF-8") from exc
    first, separator, rest = source.partition("\n")
    marker = "#vtpad-data-exchange:v1:"
    if not separator or not first.rstrip("\r").startswith(marker):
        raise _bad("CSV v1 metadata preamble is missing")
    try:
        encoded = first.rstrip("\r")[len(marker):]
        metadata = json.loads(base64.urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4)))
    except Exception as exc:
        raise _bad("CSV metadata preamble is invalid") from exc
    if not isinstance(metadata, dict) or type(metadata.get("schema_version")) is not int or metadata.get("schema_version") != 1:
        raise _bad("CSV metadata schema_version must be 1")
    definitions = _normalize_fields(metadata.get("custom_fields", []))
    try:
        reader = csv.DictReader(io.StringIO(rest, newline=""), strict=True)
        if reader.fieldnames is None or reader.fieldnames[:len(_CSV_COLUMNS)] != _CSV_COLUMNS:
            raise _bad("CSV header does not match the v1 format")
        dynamic = [f"custom_field:{field['stable_key']}" for field in definitions]
        if reader.fieldnames[len(_CSV_COLUMNS):] != dynamic:
            raise _bad("CSV custom-field columns do not match its metadata")
        rows = []
        for row in reader:
            if len(rows) >= MAX_ROWS:
                raise _bad("Import contains more than 10,000 rows")
            if None in row or any(value is None for value in row.values()):
                raise _bad("CSV row has more columns than its header")
            rows.append(row)
    except csv.Error as exc:
        raise _bad("CSV is malformed") from exc
    suites, sections, case_keys, unassigned_cases = {}, {}, set(), []
    for row in rows:
        kind = row["record_type"]
        if kind == "case" and not row["suite_key"]:
            if row["suite_name"] or row["suite_description"] or row["section_key"] or row["parent_section_key"] or row["section_name"]:
                raise _bad("unassigned CSV cases cannot reference a suite or section")
            key = _stable_key(row["case_key"], "case_key")
            if key in case_keys:
                raise _bad("case stable_key values must be unique")
            case_keys.add(key)
            try:
                tags = json.loads(row["tags"] or "[]")
                duration = int(row["estimated_duration_seconds"]) if row["estimated_duration_seconds"] else None
            except (json.JSONDecodeError, ValueError) as exc:
                raise _bad("CSV tags or duration is invalid") from exc
            values = {field["stable_key"]: _csv_cell_value(row[f"custom_field:{field['stable_key']}"], field)
                      for field in definitions}
            unassigned_cases.append(_normalize_cases([{
                "stable_key": key, "title": row["title"], "short_name": row["short_name"] or None,
                "type": row["type"] or "manual", "priority": row["priority"] or "P2",
                "text": row["text"] or None, "steps": row["steps"] or None,
                "expected_results": row["expected_results"] or None, "preconditions": row["preconditions"] or None,
                "postconditions": row["postconditions"] or None, "estimated_duration_seconds": duration,
                "tags": tags, "custom_fields": values,
            }], {"cases": len(case_keys) - 1, "case_keys": set()})[0])
            continue
        suite_key = _stable_key(row["suite_key"], "suite_key")
        suite = suites.get(suite_key)
        if kind == "suite":
            if suite is not None:
                raise _bad("CSV contains duplicate suite rows")
            suites[suite_key] = {"stable_key": suite_key,
                                 "name": _string(row["suite_name"], "suite name", required=True, max_length=500),
                                 "description": row["suite_description"] or None, "cases": [], "sections": []}
            continue
        if suite is None:
            raise _bad("CSV suite row must precede its records")
        if row["suite_name"] != suite["name"] or (row["suite_description"] or None) != suite["description"]:
            raise _bad("CSV suite metadata is inconsistent")
        if kind == "section":
            key = _stable_key(row["section_key"], "section_key")
            if key in sections:
                raise _bad("CSV section stable_key values must be unique")
            parent_key = row["parent_section_key"] or None
            parent = sections.get(parent_key) if parent_key else None
            if parent_key and (parent is None or parent["suite_key"] != suite_key):
                raise _bad("CSV section parent must precede its child and belong to the same suite")
            depth = parent["depth"] + 1 if parent else 1
            if depth > MAX_DEPTH:
                raise _bad("Import contains more than 20 section levels")
            section = {"stable_key": key, "name": _string(row["section_name"], "section name", required=True, max_length=500),
                       "description": row["section_description"] or None, "parent_key": parent_key,
                       "suite_key": suite_key, "depth": depth, "cases": [], "children": []}
            sections[key] = section
            (parent["children"] if parent else suite["sections"]).append(section)
            continue
        if kind != "case":
            raise _bad("CSV record_type must be suite, section or case")
        key = _stable_key(row["case_key"], "case_key")
        if key in case_keys:
            raise _bad("case stable_key values must be unique")
        case_keys.add(key)
        section_key = row["section_key"] or None
        section = sections.get(section_key) if section_key else None
        if section_key and (section is None or section["suite_key"] != suite_key):
            raise _bad("CSV case section must precede it and belong to the same suite")
        try:
            tags = json.loads(row["tags"] or "[]")
            duration = int(row["estimated_duration_seconds"]) if row["estimated_duration_seconds"] else None
        except (json.JSONDecodeError, ValueError) as exc:
            raise _bad("CSV tags or duration is invalid") from exc
        fields = {field["stable_key"]: _csv_cell_value(row[f"custom_field:{field['stable_key']}"], field)
                  for field in definitions}
        case = _normalize_cases([{
            "stable_key": key, "title": row["title"], "short_name": row["short_name"] or None,
            "type": row["type"] or "manual", "priority": row["priority"] or "P2",
            "text": row["text"] or None, "steps": row["steps"] or None,
            "expected_results": row["expected_results"] or None, "preconditions": row["preconditions"] or None,
            "postconditions": row["postconditions"] or None, "estimated_duration_seconds": duration,
            "tags": tags, "custom_fields": fields,
        }], {"cases": len(case_keys) - 1, "case_keys": set()})[0]
        (section["cases"] if section else suite["cases"]).append(case)
    if len(rows) != len(suites) + len(sections) + len(case_keys):
        raise _bad("CSV contains an invalid row")
    return {"schema_version": 1, "custom_fields": definitions, "suites": list(suites.values()),
            "unassigned_cases": unassigned_cases}


def _parse(fmt: Format, content: bytes) -> dict:
    _bounded_content(content)
    return _normalize_json(content) if fmt == "json" else _normalize_csv(content)


def _iter_sections(suite: dict):
    def visit(items, parent_key=None):
        for section in items:
            yield section, parent_key
            yield from visit(section["children"], section["stable_key"])
    yield from visit(suite["sections"])


def _safe_csv_text(value: str) -> str:
    offset = 0
    while offset < len(value):
        char = value[offset]
        if char.isspace() or ord(char) < 0x20:
            offset += 1
        else:
            break
    if offset < len(value) and value[offset] in "=+-@":
        return "'" + value
    return value


async def _export_data(space_id: str, suite_ids: list[str] | None) -> dict:
    query = TestSuiteModel.filter(space_id=space_id)
    if suite_ids is not None:
        query = query.filter(id__in=suite_ids)
    suites = await query.order_by("sort", "name", "id")
    if suite_ids is not None and len(suites) != len(set(suite_ids)):
        raise HTTPException(status_code=404, detail="Suite not found")
    suite_map = {}
    for index, suite in enumerate(suites, 1):
        suite_map[str(suite.id)] = {"stable_key": f"suite-{index:05d}", "name": suite.name,
                                    "description": suite.description, "cases": [], "sections": []}
    sections = await SectionModel.filter(suite_id__in=list(suite_map)).order_by("sort", "name", "id") if suite_map else []
    section_map = {}
    for index, section in enumerate(sections, 1):
        section_map[str(section.id)] = {"stable_key": f"section-{index:05d}", "name": section.name,
                                        "description": section.description, "sections": [], "cases": [],
                                        "parent_id": str(section.parent_id) if section.parent_id else None,
                                        "suite_id": str(section.suite_id)}
    for section in sections:
        seen = {str(section.id)}
        parent_id = section_map[str(section.id)]["parent_id"]
        depth = 1
        while parent_id and parent_id in section_map:
            if parent_id in seen or depth >= MAX_DEPTH:
                raise HTTPException(status_code=409, detail="Section hierarchy cannot be exported safely")
            seen.add(parent_id)
            parent_id = section_map[parent_id]["parent_id"]
            depth += 1
    for section in sections:
        data = section_map[str(section.id)]
        parent = section_map.get(data["parent_id"])
        (parent["sections"] if parent and parent["suite_id"] == data["suite_id"]
         else suite_map[data["suite_id"]]["sections"]).append(data)
    cases_query = TestCaseModel.filter(space_id=space_id)
    if suite_ids is not None:
        cases_query = cases_query.filter(suite_id__in=suite_ids)
    cases = await cases_query.order_by("sort", "id")
    unassigned_cases = []
    case_data = {}
    for index, case in enumerate(cases, 1):
        value = {"stable_key": f"case-{index:05d}", "title": case.title, "short_name": case.short_name,
                 "type": case.type.value if hasattr(case.type, "value") else case.type,
                 "priority": case.priority.value if hasattr(case.priority, "value") else case.priority,
                 "text": case.text, "steps": case.steps, "expected_results": case.expected_results,
                 "preconditions": case.preconditions, "postconditions": case.postconditions,
                 "estimated_duration_seconds": case.estimated_duration_seconds, "tags": [], "custom_fields": {}}
        case_data[str(case.id)] = value
        section = section_map.get(str(case.section_id)) if case.section_id else None
        suite = suite_map.get(str(case.suite_id)) if case.suite_id else None
        if section and suite and section["suite_id"] == str(case.suite_id):
            section["cases"].append(value)
        elif suite:
            suite["cases"].append(value)
        else:
            # A corrupt legacy cross-space suite link is not exported as a
            # foreign reference; the same-space case remains unassigned.
            unassigned_cases.append(value)
    definitions = await CustomFieldModel.filter(space_id=space_id, entity_type="testcase").order_by("sort", "name", "id")
    field_keys = {str(field.id): f"field-{index:05d}" for index, field in enumerate(definitions, 1)}
    for case in case_data.values():
        case["custom_fields"] = {key: None for key in field_keys.values()}
    if definitions and cases:
        values = await CustomFieldValueModel.filter(field_id__in=[field.id for field in definitions],
                                                    entity_id__in=[case.id for case in cases])
        for value in values:
            if str(value.entity_id) in case_data:
                case_data[str(value.entity_id)]["custom_fields"][field_keys[str(value.field_id)]] = value.value
    if cases:
        from tortoise import Tortoise
        tag_rows = await Tortoise.get_connection("default").execute_query_dict(
            "SELECT link.testcase_id, btrim(tag.title) AS name FROM test_case_tag_link_shared link "
            "JOIN tagmodel tag ON tag.id = link.tag_id "
            "JOIN test_case test_case ON test_case.id = link.testcase_id "
            "WHERE test_case.space_id = $1 AND tag.space_id = $1 "
            "AND link.testcase_id = ANY($2::uuid[]) ORDER BY lower(btrim(tag.title))",
            [uuid.UUID(str(space_id)), [case.id for case in cases]],
        )
        for row in tag_rows:
            case_data[str(row["testcase_id"])]["tags"].append(row["name"])
    def clean_section(item):
        item.pop("parent_id", None)
        item.pop("suite_id", None)
        for child in item["sections"]:
            clean_section(child)
    for suite in suite_map.values():
        for section in suite["sections"]:
            clean_section(section)
    fields = [{"stable_key": field_keys[str(field.id)], "name": field.name,
               "field_type": field.field_type.value if hasattr(field.field_type, "value") else field.field_type,
               "options": list(field.options or []), "required": field.required} for field in definitions]
    return {"schema_version": 1, "custom_fields": fields, "suites": list(suite_map.values()),
            "unassigned_cases": unassigned_cases}


def _csv_export(document: dict) -> str:
    dynamic = [f"custom_field:{field['stable_key']}" for field in document["custom_fields"]]
    metadata = json.dumps({"schema_version": 1, "custom_fields": document["custom_fields"]},
                          ensure_ascii=False, separators=(",", ":"))
    preamble = "#vtpad-data-exchange:v1:" + base64.urlsafe_b64encode(metadata.encode()).decode().rstrip("=")
    output = io.StringIO(newline="")
    output.write(preamble + "\r\n")
    writer = csv.DictWriter(output, fieldnames=_CSV_COLUMNS + dynamic, lineterminator="\r\n")
    writer.writeheader()
    def emit(base, values):
        row = dict.fromkeys(_CSV_COLUMNS + dynamic, "")
        row.update(base)
        for column in ("suite_name", "suite_description", "section_name", "section_description",
                       "section_path", "title", "short_name", "text", "steps",
                       "expected_results", "preconditions", "postconditions"):
            if isinstance(row.get(column), str):
                row[column] = _safe_csv_text(row[column])
        for field in document["custom_fields"]:
            value = values.get(field["stable_key"])
            if value is None:
                cell = ""
            else:
                validate_value(_field_like(field), value)
                if field["field_type"] == "text":
                    cell = json.dumps(_safe_csv_text(value), ensure_ascii=False)
                else:
                    cell = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
            row[f"custom_field:{field['stable_key']}"] = cell
        writer.writerow(row)
    def case_base(case, suite, section_key="", path=""):
        base = {"record_type": "case", "suite_key": suite["stable_key"], "suite_name": suite["name"],
                "suite_description": suite["description"] or "", "section_key": section_key,
                "section_path": _safe_csv_text(path), "case_key": case["stable_key"], "title": _safe_csv_text(case["title"]),
                "short_name": _safe_csv_text(case["short_name"] or ""), "type": case["type"], "priority": case["priority"],
                "estimated_duration_seconds": case["estimated_duration_seconds"] if case["estimated_duration_seconds"] is not None else "",
                "tags": json.dumps(case["tags"], ensure_ascii=False, separators=(",", ":"))}
        for name in ("text", "steps", "expected_results", "preconditions", "postconditions"):
            base[name] = _safe_csv_text(case[name] or "")
        return base
    for suite in document["suites"]:
        emit({"record_type": "suite", "suite_key": suite["stable_key"], "suite_name": _safe_csv_text(suite["name"]),
              "suite_description": _safe_csv_text(suite["description"] or "")}, {})
        def visit(sections, parent_key=None, path=()):
            for section in sections:
                current = path + (section["name"],)
                emit({"record_type": "section", "suite_key": suite["stable_key"], "suite_name": suite["name"],
                      "suite_description": suite["description"] or "", "section_key": section["stable_key"],
                      "parent_section_key": parent_key or "", "section_name": _safe_csv_text(section["name"]),
                      "section_description": _safe_csv_text(section["description"] or ""),
                      "section_path": _safe_csv_text(" / ".join(current))}, {})
                for case in section["cases"]:
                    emit(case_base(case, suite, section["stable_key"], " / ".join(current)), case["custom_fields"])
                visit(section["sections"], section["stable_key"], current)
        visit(suite["sections"])
        for case in suite["cases"]:
            emit(case_base(case, suite), case["custom_fields"])
    for case in document.get("unassigned_cases", []):
        emit(case_base(case, {"stable_key": "", "name": "", "description": ""}), case["custom_fields"])
    return output.getvalue()


async def export_content(space_id, fmt: Format, request, suite_ids: list[uuid.UUID] | None = None) -> dict:
    fmt = _check_format(fmt)
    await _authorize(space_id, request)
    selected_suites = None
    if suite_ids is not None:
        try:
            selected_suites = [uuid.UUID(str(value)) for value in suite_ids]
        except (ValueError, TypeError, AttributeError) as exc:
            raise HTTPException(status_code=404, detail="Suite not found") from exc
    document = await _export_data(str(space_id), selected_suites)
    content = json.dumps(document, ensure_ascii=False, separators=(",", ":")) if fmt == "json" else _csv_export(document)
    return {"content": content, "media_type": "application/json" if fmt == "json" else "text/csv; charset=utf-8",
            "filename": f"vtpad-space-export.{fmt}", "schema_version": 1, "suite_count": len(document["suites"])}


def _validate_document(document: dict) -> dict:
    flat = _flatten(document["suites"])
    flat["cases"].extend({**case, "suite_key": None, "section_key": None}
                         for case in document.get("unassigned_cases", []))
    fields_by_key = {field["stable_key"]: field for field in document["custom_fields"]}
    case_by_key = {case["stable_key"]: case for case in flat["cases"]}
    if len(case_by_key) != len(flat["cases"]):
        raise _bad("case stable_key values must be unique")
    for case in flat["cases"]:
        if set(case["custom_fields"]) - set(fields_by_key):
            raise _bad("case references an unknown custom-field stable_key")
        for field in document["custom_fields"]:
            validate_value(_field_like(field), case["custom_fields"].get(field["stable_key"]),
                           enforce_required=field["required"])
    names = [case["short_name"].strip().lower() for case in flat["cases"] if case["short_name"]]
    if len(names) != len(set(names)):
        raise _bad("Import contains duplicate testcase short_name values")
    return {**document, "flat": flat, "fields_by_key": fields_by_key}


async def _conflicts(space_id: str, document: dict, connection=None) -> list[str]:
    names = [case["short_name"].strip() for case in document["flat"]["cases"] if case["short_name"]]
    if not names:
        return []
    from tortoise import Tortoise
    conn = connection or Tortoise.get_connection("default")
    rows = await conn.execute_query_dict(
        "SELECT short_name FROM test_case WHERE space_id = $1 AND lower(short_name) = ANY($2::text[])",
        [uuid.UUID(str(space_id)), sorted({name.lower() for name in names})],
    )
    existing_norm = {row["short_name"].lower() for row in rows if row["short_name"]}
    return sorted({name for name in names if name.lower() in existing_norm}, key=str.lower)


async def _required_field_conflicts(space_id: str, document: dict, connection=None) -> list[str]:
    if not document["flat"]["cases"]:
        return []
    query = CustomFieldModel.filter(space_id=space_id, entity_type=CustomFieldEntityType.testcase, required=True)
    if connection is not None:
        query = query.using_db(connection)
    return sorted(await query.values_list("name", flat=True), key=str.casefold)


def _preview_case(case: dict, fields: list[dict]) -> dict:
    return {"stable_key": case["stable_key"], "title": html.escape(case["title"]),
            "short_name": html.escape(case["short_name"] or ""), "type": case["type"], "priority": case["priority"],
            "tags": [html.escape(tag) for tag in case["tags"]], "text": html.escape(case["text"] or ""),
            "steps": html.escape(case["steps"] or ""), "expected_results": html.escape(case["expected_results"] or ""),
            "preconditions": html.escape(case["preconditions"] or ""),
            "custom_fields": [{"name": html.escape(field["name"]),
                               "value": html.escape(case["custom_fields"][field["stable_key"]])
                               if isinstance(case["custom_fields"].get(field["stable_key"]), str)
                               else case["custom_fields"].get(field["stable_key"])} for field in fields]}


async def preview_import(space_id, fmt: Format, content: bytes, request) -> dict:
    fmt = _check_format(fmt)
    await _authorize(space_id, request)
    document = _validate_document(_parse(fmt, content))
    conflicts = await _conflicts(str(space_id), document)
    required_field_conflicts = await _required_field_conflicts(str(space_id), document)
    return {"valid": not conflicts and not required_field_conflicts, "schema_version": 1, "suite_count": len(document["suites"]),
            "section_count": len(document["flat"]["sections"]), "case_count": len(document["flat"]["cases"]),
            "custom_field_count": len(document["custom_fields"]), "short_name_conflicts": conflicts,
            "required_field_conflicts": required_field_conflicts,
            "suites": [{"stable_key": suite["stable_key"], "name": html.escape(suite["name"]),
                        "case_count": sum(1 for case in document["flat"]["cases"] if case["suite_key"] == suite["stable_key"]),
                        "sections": _suite_sections(suite)} for suite in document["suites"]],
            "cases": [_preview_case(case, document["custom_fields"]) for case in document["flat"]["cases"][:100]],
            "cases_truncated": len(document["flat"]["cases"]) > 100}


def _suite_sections(suite: dict) -> list[dict]:
    result = []
    def visit(items, parent=None):
        for section in items:
            result.append({"stable_key": section["stable_key"], "name": html.escape(section["name"]),
                           "parent_key": parent})
            visit(section["children"], section["stable_key"])
    visit(suite["sections"])
    return result


async def _receipt_outcome(receipt: ImportReceiptModel, digest: str, actor_id: uuid.UUID, space_id: uuid.UUID) -> dict:
    if receipt.content_hash != digest or receipt.actor_id != actor_id or receipt.space_id != space_id:
        raise HTTPException(status_code=409, detail="Idempotency key is already bound to another import")
    return {**receipt.response, "replayed": True}


async def import_content(space_id, fmt: Format, content: bytes, idempotency_key: str, request) -> dict:
    fmt = _check_format(fmt)
    _bounded_content(content)
    if not isinstance(idempotency_key, str) or not idempotency_key.strip() or len(idempotency_key) > 200:
        raise _bad("Idempotency-Key must contain 1 to 200 characters")
    document = _validate_document(_parse(fmt, content))
    write_capabilities = []
    if document["suites"]:
        write_capabilities.append("suites")
    if document["flat"]["sections"]:
        write_capabilities.append("sections")
    if document["flat"]["cases"] or document["custom_fields"]:
        write_capabilities.append("cases")
    if any(case["tags"] for case in document["flat"]["cases"]):
        write_capabilities.append("tags")
    if not write_capabilities:
        # Even an otherwise empty import records an idempotency receipt.
        write_capabilities.append("cases")
    actor_id = await _authorize(space_id, request, write_capabilities=tuple(write_capabilities))
    digest = hashlib.sha256(bytes(content)).hexdigest()
    space_uuid = uuid.UUID(str(space_id))
    receipt = await ImportReceiptModel.get_or_none(
        idempotency_key=idempotency_key, actor_id=actor_id, space_id=space_uuid
    )
    if receipt:
        return await _receipt_outcome(receipt, digest, actor_id, space_uuid)
    try:
        async with in_transaction() as connection:
            target = await SpaceModel.filter(id=space_uuid).using_db(connection).select_for_update().first()
            if not target:
                raise HTTPException(status_code=404, detail="Space not found")
            receipt = await ImportReceiptModel.filter(
                idempotency_key=idempotency_key, actor_id=actor_id, space_id=space_uuid
            ).using_db(connection).first()
            if receipt:
                # Check receipt in this transaction; the outer retry handles embeddings.
                if receipt.content_hash != digest or receipt.actor_id != actor_id or receipt.space_id != space_uuid:
                    raise HTTPException(status_code=409, detail="Idempotency key is already bound to another import")
                response = {**receipt.response, "replayed": True}
            else:
                conflicts = await _conflicts(str(space_uuid), document, connection)
                if conflicts:
                    raise _bad("Target space already contains one or more testcase short_name values")
                required_conflicts = await _required_field_conflicts(str(space_uuid), document, connection)
                if required_conflicts:
                    raise _bad("Target space has required testcase custom fields that this file cannot populate")
                suite_ids, section_ids, case_ids, field_ids = {}, {}, {}, {}
                for field_sort, definition in enumerate(document["custom_fields"], 1):
                    field = await CustomFieldModel.create(
                        name=definition["name"], field_type=definition["field_type"],
                        entity_type=CustomFieldEntityType.testcase, options=definition["options"],
                        required=definition["required"], sort=field_sort * 10,
                        space_id=space_uuid, created_by_id=actor_id,
                        using_db=connection)
                    field_ids[definition["stable_key"]] = field.id
                for suite_sort, suite in enumerate(document["suites"], 1):
                    model = await TestSuiteModel.create(name=suite["name"], description=suite["description"],
                                                        sort=suite_sort * 10, space_id=space_uuid,
                                                        created_by_id=actor_id, using_db=connection)
                    suite_ids[suite["stable_key"]] = model.id
                for suite in document["suites"]:
                    section_sorts = {}
                    for section, parent_key in _iter_sections(suite):
                        parent_sort_key = parent_key or "__root__"
                        section_sorts[parent_sort_key] = section_sorts.get(parent_sort_key, 0) + 1
                        model = await SectionModel.create(
                            name=section["name"], description=section["description"],
                            suite_id=suite_ids[suite["stable_key"]], parent_id=section_ids.get(parent_key),
                            sort=section_sorts[parent_sort_key] * 10,
                            created_by_id=actor_id, using_db=connection)
                        section_ids[section["stable_key"]] = model.id
                case_sorts = {}
                for case in document["flat"]["cases"]:
                    group_key = (case["suite_key"], case["section_key"])
                    case_sorts[group_key] = case_sorts.get(group_key, 0) + 1
                    model = await TestCaseModel.create(
                        title=case["title"], text=case["text"], steps=case["steps"],
                        expected_results=case["expected_results"], preconditions=case["preconditions"],
                        postconditions=case["postconditions"],
                        estimated_duration_seconds=case["estimated_duration_seconds"],
                        type=case["type"], status=TestCaseStatus.draft, priority=case["priority"],
                        sort=case_sorts[group_key] * 10, short_name=case["short_name"], space_id=space_uuid,
                        suite_id=suite_ids.get(case["suite_key"]),
                        section_id=section_ids.get(case["section_key"]) if case["suite_key"] else None,
                        created_by_id=actor_id, using_db=connection)
                    case_ids[case["stable_key"]] = model.id
                    await TestCaseService._replace_tags(str(model.id), str(space_uuid), case["tags"], connection)
                    await TestCaseService._create_test_case_version(model, str(actor_id), connection=connection)
                    for definition in document["custom_fields"]:
                        value = validate_value(_field_like(definition),
                                               case["custom_fields"].get(definition["stable_key"]),
                                               enforce_required=definition["required"])
                        if value is not None:
                            await CustomFieldValueModel.create(
                                field_id=field_ids[definition["stable_key"]], entity_id=model.id,
                                value=value, using_db=connection)
                response = {"schema_version": 1, "suite_count": len(suite_ids),
                            "section_count": len(section_ids), "case_count": len(case_ids),
                            "custom_field_count": len(field_ids),
                            "id_map": {
                                "suites": {key: str(value) for key, value in suite_ids.items()},
                                "sections": {key: str(value) for key, value in section_ids.items()},
                                "cases": {key: str(value) for key, value in case_ids.items()},
                                "custom_fields": {key: str(value) for key, value in field_ids.items()},
                            },
                            "created_case_ids": [str(value) for value in case_ids.values()],
                            "replayed": False}
                receipt = await ImportReceiptModel.create(
                    idempotency_key=idempotency_key, content_hash=digest, actor_id=actor_id,
                    space_id=space_uuid, response={key: value for key, value in response.items() if key != "replayed"},
                    created_case_ids=response["created_case_ids"], embeddings_pending=False, using_db=connection)
        return response
    except IntegrityError:
        receipt = await ImportReceiptModel.get_or_none(
            idempotency_key=idempotency_key, actor_id=actor_id, space_id=space_uuid
        )
        if receipt:
            return await _receipt_outcome(receipt, digest, actor_id, space_uuid)
        raise

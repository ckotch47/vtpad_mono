import json
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from ..custom_field.dto import CustomFieldValueInput

MAX_TEMPLATE_TEXT_CHARS = 32_768
MAX_TEMPLATE_CONTENT_BYTES = 128 * 1024
MAX_TEMPLATE_DESCRIPTION_CHARS = 4_096
MAX_TEMPLATE_VERSIONS = 100
MAX_VERSION_PAGE_SIZE = 50
MAX_ESTIMATED_DURATION_SECONDS = 2_147_483_647


def _check_serialized_content(values: dict) -> None:
    content = {key: value for key, value in values.items() if key in {
        'title', 'text', 'preconditions', 'steps', 'expected_results',
        'postconditions', 'type', 'priority', 'estimated_duration_seconds',
    }}
    size = len(json.dumps(content, ensure_ascii=False, separators=(',', ':')).encode('utf-8'))
    if size > MAX_TEMPLATE_CONTENT_BYTES:
        raise ValueError('template content exceeds the maximum serialized size')


class CaseTemplateFieldsDto(BaseModel):
    model_config = ConfigDict(extra='forbid')

    title: str = Field(min_length=1, max_length=500)
    text: str | None = Field(default=None, max_length=MAX_TEMPLATE_TEXT_CHARS)
    preconditions: str | None = Field(default=None, max_length=MAX_TEMPLATE_TEXT_CHARS)
    steps: str | None = Field(default=None, max_length=MAX_TEMPLATE_TEXT_CHARS)
    expected_results: str | None = Field(default=None, max_length=MAX_TEMPLATE_TEXT_CHARS)
    postconditions: str | None = Field(default=None, max_length=MAX_TEMPLATE_TEXT_CHARS)
    type: Literal['manual', 'checklist', 'automated'] = 'manual'
    priority: Literal['P0', 'P1', 'P2', 'P3'] = 'P2'
    estimated_duration_seconds: int | None = Field(default=None, ge=0, le=MAX_ESTIMATED_DURATION_SECONDS)

    @field_validator('title')
    @classmethod
    def title_must_have_non_whitespace(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError('title cannot be blank')
        return normalized

    @model_validator(mode='after')
    def content_size_is_bounded(self):
        _check_serialized_content(self.model_dump())
        return self


class CaseTemplateCreateDto(BaseModel):
    model_config = ConfigDict(extra='forbid')

    name: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=MAX_TEMPLATE_DESCRIPTION_CHARS)
    fields: CaseTemplateFieldsDto

    @field_validator('name')
    @classmethod
    def normalize_name(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError('name cannot be blank')
        return normalized


class CaseTemplateUpdateDto(CaseTemplateCreateDto):
    pass


class CaseTemplateOverridesDto(BaseModel):
    model_config = ConfigDict(extra='forbid')

    text: str | None = Field(default=None, max_length=MAX_TEMPLATE_TEXT_CHARS)
    preconditions: str | None = Field(default=None, max_length=MAX_TEMPLATE_TEXT_CHARS)
    steps: str | None = Field(default=None, max_length=MAX_TEMPLATE_TEXT_CHARS)
    expected_results: str | None = Field(default=None, max_length=MAX_TEMPLATE_TEXT_CHARS)
    postconditions: str | None = Field(default=None, max_length=MAX_TEMPLATE_TEXT_CHARS)
    type: Literal['manual', 'checklist', 'automated'] | None = None
    priority: Literal['P0', 'P1', 'P2', 'P3'] | None = None
    estimated_duration_seconds: int | None = Field(default=None, ge=0, le=MAX_ESTIMATED_DURATION_SECONDS)

    @model_validator(mode='after')
    def content_size_is_bounded(self):
        _check_serialized_content(self.model_dump(exclude_none=True))
        return self


class CaseTemplateUseDto(BaseModel):
    model_config = ConfigDict(extra='forbid')

    title: str = Field(min_length=1, max_length=500)
    suite_id: UUID | None = None
    section_id: UUID | None = None
    version_number: int | None = Field(default=None, ge=1, le=MAX_TEMPLATE_VERSIONS)
    overrides: CaseTemplateOverridesDto = Field(default_factory=CaseTemplateOverridesDto)
    custom_fields: list[CustomFieldValueInput] | None = Field(default=None, max_length=50)

    @field_validator('title')
    @classmethod
    def title_must_have_non_whitespace(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError('title cannot be blank')
        return normalized

    @field_validator('custom_fields')
    @classmethod
    def custom_field_values_are_bounded(cls, values):
        if values is not None:
            try:
                serialized = json.dumps(
                    [item.model_dump(mode='json') for item in values],
                    ensure_ascii=False, separators=(',', ':'),
                ).encode('utf-8')
            except (TypeError, ValueError, RecursionError) as exc:
                raise ValueError('custom field values must be JSON serializable') from exc
            if len(serialized) > 64 * 1024:
                raise ValueError('custom field values exceed the maximum serialized size')
        return values


class CaseTemplateVersionQueryDto(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=MAX_VERSION_PAGE_SIZE)

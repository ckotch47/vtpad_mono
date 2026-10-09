from fastapi import APIRouter, Depends, HTTPException, Query, Request

from ..common.crypto import bearer
from .service import MAX_BYTES, export_content, import_content, preview_import

router = APIRouter(prefix="/v2/data-exchange/space/{space_id}", tags=["data-exchange"])


async def _read_bounded_body(request: Request, format: str) -> bytes:
    expected_types = {"json": "application/json", "csv": "text/csv"}
    expected_type = expected_types.get(format)
    if expected_type is None:
        raise HTTPException(status_code=415, detail="format must be json or csv")
    content_type = request.headers.get("content-type", "").split(";", 1)[0].strip().lower()
    if content_type != expected_type:
        raise HTTPException(status_code=415, detail=f"Content-Type must be {expected_type}")
    content_length = request.headers.get("content-length")
    if content_length:
        try:
            if int(content_length) > MAX_BYTES:
                raise HTTPException(status_code=413, detail="Import content exceeds the 5 MiB limit")
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Invalid Content-Length") from exc

    body = bytearray()
    async for chunk in request.stream():
        body.extend(chunk)
        if len(body) > MAX_BYTES:
            raise HTTPException(status_code=413, detail="Import content exceeds the 5 MiB limit")
    return bytes(body)


@router.get("/export", dependencies=[Depends(bearer)])
async def export_space_data(
    space_id: str,
    request: Request,
    format: str = "json",
    suite_ids: list[str] | None = Query(default=None),
):
    return await export_content(space_id, format, request, suite_ids)


@router.post("/preview", dependencies=[Depends(bearer)])
async def preview_space_import(space_id: str, request: Request, format: str = "json"):
    return await preview_import(space_id, format, await _read_bounded_body(request, format), request)


@router.post("/import", dependencies=[Depends(bearer)])
async def import_space_data(space_id: str, request: Request, format: str = "json"):
    idempotency_key = request.headers.get("Idempotency-Key", "")
    return await import_content(
        space_id, format, await _read_bounded_body(request, format), idempotency_key, request
    )

from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile, status
from pydantic import BaseModel

from app.core.index_state import set_current_index
from app.core.pages import DataValidationError, PageManager


router = APIRouter(tags=["data"])
_page_manager: PageManager | None = None
_upload_generation = 0


class PageRecordsResponse(BaseModel):
    id: int
    total_records: int
    offset: int
    limit: int
    records: list[str]
    has_previous: bool
    has_next: bool


def get_page_manager() -> PageManager:
    if _page_manager is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Nenhum arquivo foi carregado.",
        )
    return _page_manager


@router.post("/data/load")
async def load_data(
    file: UploadFile = File(...),
    page_size: int = Form(...),
) -> dict[str, object]:
    global _page_manager, _upload_generation

    if not file.filename or not file.filename.lower().endswith(".txt"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Envie um arquivo com extensão .txt.",
        )

    _upload_generation += 1
    upload_generation = _upload_generation
    content = await file.read()

    try:
        page_manager = PageManager.from_txt(content, page_size)
    except DataValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    if upload_generation != _upload_generation:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Carregamento substituído por uma solicitação mais recente.",
        )

    _page_manager = page_manager
    # Um índice construído para outro conjunto de páginas não pode ser reutilizado.
    set_current_index(None)
    return _page_manager.summary()


@router.get("/pages/summary")
def pages_summary() -> dict[str, object]:
    return get_page_manager().summary()


@router.get("/pages/{page_id}/records", response_model=PageRecordsResponse)
def get_page_records(
    page_id: int,
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
) -> PageRecordsResponse:
    try:
        page = get_page_manager().get_page(page_id)
    except DataValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    total_records = len(page.records)
    if offset > total_records:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"O deslocamento deve estar entre zero e {total_records}.",
        )

    records = page.records[offset : offset + limit]
    return PageRecordsResponse(
        id=page.id,
        total_records=total_records,
        offset=offset,
        limit=limit,
        records=records,
        has_previous=offset > 0,
        has_next=offset + limit < total_records,
    )


@router.get("/pages/{page_id}")
def get_page(page_id: int) -> dict:
    try:
        return get_page_manager().get_page(page_id).to_dict()
    except DataValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.core.pages import DataValidationError, PageManager


router = APIRouter(tags=["data"])
_page_manager: PageManager | None = None


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
    global _page_manager

    if not file.filename or not file.filename.lower().endswith(".txt"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Envie um arquivo com extensão .txt.",
        )

    try:
        _page_manager = PageManager.from_txt(await file.read(), page_size)
    except DataValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return _page_manager.summary()


@router.get("/pages/summary")
def pages_summary() -> dict[str, object]:
    return get_page_manager().summary()


@router.get("/pages/{page_id}")
def get_page(page_id: int) -> dict:
    try:
        return get_page_manager().get_page(page_id).to_dict()
    except DataValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

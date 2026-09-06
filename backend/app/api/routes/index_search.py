from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, field_validator

from app.api.routes.data import get_page_manager
from app.core.index_state import get_current_index, set_current_index
from app.core.search import SearchIndex, search_by_index


router = APIRouter(tags=["search"])


class IndexSearchRequest(BaseModel):
    key: str

    @field_validator("key")
    @classmethod
    def validate_key(cls, key: str) -> str:
        key = key.strip()
        if not key:
            raise ValueError("Informe uma chave de busca.")
        return key


class IndexSearchResponse(BaseModel):
    found: bool
    key: str
    bucket_id: int
    page_id: int | None
    pages_read: int
    elapsed_time: float
    trace: list[str]


def set_hash_index(index: SearchIndex | None) -> None:
    """Mantém o contrato usado pela futura rota de construção do índice."""
    set_current_index(index)


def get_hash_index() -> SearchIndex:
    index = get_current_index()
    if index is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="O índice ainda não foi construído.",
        )
    return index


@router.post("/search/index", response_model=IndexSearchResponse)
def index_search(request: IndexSearchRequest) -> IndexSearchResponse:
    result = search_by_index(
        request.key,
        get_hash_index(),
        get_page_manager(),
    )
    return IndexSearchResponse.model_validate(result.to_dict())

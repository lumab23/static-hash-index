from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, field_validator

from app.api.routes.data import get_page_manager
from app.core.search import SearchIndex, search_by_index


router = APIRouter(tags=["search"])
_hash_index: SearchIndex | None = None


class IndexSearchRequest(BaseModel):
    key: str

    @field_validator("key")
    @classmethod
    def validate_key(cls, key: str) -> str:
        key = key.strip()
        if not key:
            raise ValueError("Informe uma chave de busca.")
        return key


def set_hash_index(index: SearchIndex | None) -> None:
    global _hash_index
    _hash_index = index


def get_hash_index() -> SearchIndex:
    if _hash_index is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="O índice ainda não foi construído.",
        )
    return _hash_index


@router.post("/search/index")
def index_search(request: IndexSearchRequest) -> dict[str, Any]:
    result = search_by_index(
        request.key,
        get_hash_index(),
        get_page_manager(),
    )
    return result.to_dict()

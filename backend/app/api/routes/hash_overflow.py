from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel

from app.core.hash_index import HashIndex
from app.core.index_state import get_current_index


router = APIRouter(tags=["index"])


class HashOverflowResponse(BaseModel):
    key: str
    bucket_id: int
    bucket_capacity: int
    bucket_occupancy: int
    collision_count: int
    collision_rate: float
    overflow_bucket_count: int
    overflow_rate: float
    overflow_entries: list[str]


@router.get("/index/hash-overflow", response_model=HashOverflowResponse)
def hash_overflow(key: str = Query(..., min_length=1)) -> HashOverflowResponse:
    if not key.strip():
        raise HTTPException(status_code=422, detail="Informe uma chave.")
    index = get_current_index()
    if not isinstance(index, HashIndex) or index.nb == 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="O índice ainda não foi construído.",
        )
    return HashOverflowResponse.model_validate(index.hash_overflow_details(key))

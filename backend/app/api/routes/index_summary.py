from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.core.hash_index import HashIndex
from app.core.index_state import get_current_index


router = APIRouter(tags=["index"])


class IndexSummaryResponse(BaseModel):
    fr: int
    nb: int
    total_indexed: int
    build_time: float


@router.get("/index/summary", response_model=IndexSummaryResponse)
def index_summary() -> IndexSummaryResponse:
    index = get_current_index()
    if not isinstance(index, HashIndex) or index.nb == 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="O índice ainda não foi construído.",
        )
    return IndexSummaryResponse(
        fr=index.bucket_capacity,
        nb=index.nb,
        total_indexed=index.total_indexed,
        build_time=index.build_time,
    )

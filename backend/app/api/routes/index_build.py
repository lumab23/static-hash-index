from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.api.routes.data import get_page_manager
from app.api.routes.index_summary import IndexSummaryResponse
from app.core.hash_function import hash_key
from app.core.hash_index import HashIndex
from app.core.index_state import set_current_index
from app.core.overflow import OverflowBlock


router = APIRouter(tags=["index"])


class IndexBuildRequest(BaseModel):
    fr: int = Field(strict=True, gt=0)


@router.post("/index/build", response_model=IndexSummaryResponse)
def index_build(request: IndexBuildRequest) -> IndexSummaryResponse:
    pages = get_page_manager().pages
    index = HashIndex(request.fr, hash_key, OverflowBlock)
    index.build(pages)
    set_current_index(index)
    return IndexSummaryResponse(
        fr=index.bucket_capacity,
        nb=index.nb,
        total_indexed=index.total_indexed,
        build_time=index.build_time,
    )

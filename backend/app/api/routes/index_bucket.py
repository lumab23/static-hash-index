from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.core.hash_index import HashIndex
from app.core.index_state import get_current_index


router = APIRouter(tags=["index"])


class EntryResponse(BaseModel):
    key: str
    page_id: int


class OverflowBlockResponse(BaseModel):
    block: int
    count: int
    entries: list[EntryResponse]


class BucketResponse(BaseModel):
    id: int
    capacity: int
    primary_count: int
    primary_entries: list[EntryResponse]
    has_overflow: bool
    overflow_blocks: list[OverflowBlockResponse]
    total_entries: int


@router.get("/index/buckets/{bucket_id}", response_model=BucketResponse)
def index_bucket(bucket_id: int) -> BucketResponse:
    index = get_current_index()
    if not isinstance(index, HashIndex) or index.nb == 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="O índice ainda não foi construído.",
        )
    try:
        bucket = index.get_bucket(bucket_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bucket {bucket_id} não encontrado.",
        ) from exc

    primary_entries = [
        EntryResponse(key=entry.key, page_id=entry.page_id)
        for entry in bucket.entries
    ]
    overflow_blocks = []
    total_entries = len(primary_entries)
    block = bucket.overflow
    while block is not None:
        entries = [
            EntryResponse(key=entry.key, page_id=entry.page_id)
            for entry in block.entries
        ]
        overflow_blocks.append(
            OverflowBlockResponse(
                block=len(overflow_blocks) + 1, count=len(entries), entries=entries
            )
        )
        total_entries += len(entries)
        block = block.next

    return BucketResponse(
        id=bucket.id,
        capacity=bucket.capacity,
        primary_count=len(primary_entries),
        primary_entries=primary_entries,
        has_overflow=bucket.overflow is not None,
        overflow_blocks=overflow_blocks,
        total_entries=total_entries,
    )

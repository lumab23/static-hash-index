from dataclasses import asdict, dataclass
from time import perf_counter
from typing import Protocol

from app.core.pages import PageManager


class IndexEntry(Protocol):
    key: str
    page_id: int


class SearchBucket(Protocol):
    def find(self, key: str) -> IndexEntry | None: ...


class SearchIndex(Protocol):
    def bucket_id_for(self, key: str) -> int: ...

    def get_bucket(self, bucket_id: int) -> SearchBucket: ...


@dataclass
class SearchResult:
    found: bool
    key: str
    bucket_id: int
    page_id: int | None
    pages_read: int
    elapsed_time: float
    trace: list[str]

    def to_dict(self) -> dict:
        return asdict(self)


def search_by_index(
    key: str,
    index: SearchIndex,
    page_manager: PageManager,
) -> SearchResult:
    started_at = perf_counter()
    bucket_id = index.bucket_id_for(key)
    bucket = index.get_bucket(bucket_id)
    entry = bucket.find(key)
    trace = [f"Chave '{key}'", f"Bucket {bucket_id}"]

    if entry is None:
        trace.append("Chave não encontrada no bucket")
        return SearchResult(
            found=False,
            key=key,
            bucket_id=bucket_id,
            page_id=None,
            pages_read=0,
            elapsed_time=perf_counter() - started_at,
            trace=trace,
        )

    page = page_manager.get_page(entry.page_id)
    found = key in page.records
    trace.extend([f"Página {page.id}", "Chave confirmada" if found else "Chave não confirmada"])

    return SearchResult(
        found=found,
        key=key,
        bucket_id=bucket_id,
        page_id=page.id,
        pages_read=1,
        elapsed_time=perf_counter() - started_at,
        trace=trace,
    )

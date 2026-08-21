from dataclasses import dataclass

from app.core.pages import PageManager
from app.core.search import search_by_index


@dataclass
class FakeEntry:
    key: str
    page_id: int


class FakeBucket:
    def __init__(
        self,
        entries: list[FakeEntry],
        overflow: list[FakeEntry] | None = None,
    ) -> None:
        self.entries = entries
        self.overflow = overflow or []

    def find(self, key: str) -> FakeEntry | None:
        for entry in self.entries + self.overflow:
            if entry.key == key:
                return entry
        return None


class FakeIndex:
    def __init__(self, buckets: list[FakeBucket]) -> None:
        self.buckets = buckets

    def bucket_id_for(self, key: str) -> int:
        return len(key) % len(self.buckets)

    def get_bucket(self, bucket_id: int) -> FakeBucket:
        return self.buckets[bucket_id]


def make_index() -> FakeIndex:
    return FakeIndex(
        [
            FakeBucket([], [FakeEntry("lambda", 1)]),
            FakeBucket([FakeEntry("beta", 0)]),
            FakeBucket([]),
        ]
    )


def test_finds_key_and_confirms_it_in_data_page() -> None:
    pages = PageManager(["alpha", "beta", "gamma", "lambda"], 2)

    result = search_by_index("beta", make_index(), pages)

    assert result.found is True
    assert result.bucket_id == 1
    assert result.page_id == 0
    assert result.pages_read == 1
    assert result.elapsed_time >= 0
    assert result.trace[-1] == "Chave confirmada"


def test_finds_key_stored_in_overflow() -> None:
    pages = PageManager(["alpha", "beta", "gamma", "lambda"], 2)

    result = search_by_index("lambda", make_index(), pages)

    assert result.found is True
    assert result.bucket_id == 0
    assert result.page_id == 1
    assert result.pages_read == 1


def test_reports_missing_key_without_reading_data_page() -> None:
    pages = PageManager(["alpha", "beta", "gamma", "lambda"], 2)

    result = search_by_index("missing", make_index(), pages)

    assert result.found is False
    assert result.page_id is None
    assert result.pages_read == 0


def test_rejects_index_entry_that_points_to_wrong_page() -> None:
    pages = PageManager(["alpha", "beta", "gamma", "lambda"], 2)
    index = FakeIndex([FakeBucket([FakeEntry("alpha", 1)])])

    result = search_by_index("alpha", index, pages)

    assert result.found is False
    assert result.page_id == 1
    assert result.pages_read == 1
    assert result.trace[-1] == "Chave não confirmada"

import pytest

from app.core.bucket import IndexEntry
from app.core.hash_index import HashIndex, calculate_bucket_count
from app.core.pages import Page, PageManager
from app.core.search import search_by_index


@pytest.mark.parametrize(
    "total_records, bucket_capacity, expected",
    [(10, 2, 6), (10, 3, 4), (0, 2, 1), (2, 10, 1)],
)
def test_calculates_bucket_count(
    total_records: int, bucket_capacity: int, expected: int
) -> None:
    assert calculate_bucket_count(total_records, bucket_capacity) == expected


@pytest.mark.parametrize("bucket_capacity", [0, -1])
def test_rejects_non_positive_capacity(bucket_capacity: int) -> None:
    with pytest.raises(ValueError):
        calculate_bucket_count(10, bucket_capacity)


def test_rejects_negative_record_count() -> None:
    with pytest.raises(ValueError):
        calculate_bucket_count(-1, 2)


@pytest.mark.parametrize("total_records", [None, "10", 10.0, True, False])
def test_rejects_invalid_record_count_type(total_records: object) -> None:
    with pytest.raises(TypeError):
        calculate_bucket_count(total_records, 2)


@pytest.mark.parametrize("bucket_capacity", [None, "2", 2.0, True, False])
def test_rejects_invalid_capacity_type(bucket_capacity: object) -> None:
    with pytest.raises(TypeError):
        calculate_bucket_count(10, bucket_capacity)


@pytest.mark.parametrize("total_records", [0, 1, 10, 11, 100])
@pytest.mark.parametrize("bucket_capacity", [1, 2, 3, 10])
def test_bucket_count_is_strictly_greater_than_ratio(
    total_records: int, bucket_capacity: int
) -> None:
    nb = calculate_bucket_count(total_records, bucket_capacity)

    assert nb > total_records / bucket_capacity


def test_handles_large_integers_without_rounding() -> None:
    total_records = 10**30
    bucket_capacity = 3

    nb = calculate_bucket_count(total_records, bucket_capacity)

    assert nb * bucket_capacity > total_records
    assert (nb - 1) * bucket_capacity <= total_records


class FakeOverflow:
    def __init__(self, capacity: int) -> None:
        self.capacity = capacity
        self.entries: list[IndexEntry] = []
        self.next = None

    def add(self, entry: IndexEntry) -> None:
        self.entries.append(entry)


def fake_hash(key: str, nb: int) -> int:
    return len(key) % nb


def test_index_initial_state() -> None:
    index = HashIndex(2, fake_hash, FakeOverflow)

    assert index.bucket_capacity == 2
    assert index.nb == 0
    assert index.buckets == []
    assert index.total_indexed == 0
    assert index.build_time == 0.0
    with pytest.raises(RuntimeError, match="não foi construído"):
        index.bucket_id_for("apple")
    with pytest.raises(RuntimeError, match="não foi construído"):
        index.get_bucket(0)


@pytest.mark.parametrize("capacity", [None, "2", 2.0, True, False])
def test_index_rejects_invalid_capacity_type(capacity: object) -> None:
    with pytest.raises(TypeError):
        HashIndex(capacity, fake_hash, FakeOverflow)


@pytest.mark.parametrize("capacity", [0, -1])
def test_index_rejects_non_positive_capacity(capacity: int) -> None:
    with pytest.raises(ValueError):
        HashIndex(capacity, fake_hash, FakeOverflow)


@pytest.mark.parametrize("dependency", [None, 1, "function"])
def test_index_rejects_non_callable_dependencies(dependency: object) -> None:
    with pytest.raises(TypeError):
        HashIndex(2, dependency, FakeOverflow)
    with pytest.raises(TypeError):
        HashIndex(2, fake_hash, dependency)


def test_builds_one_page_and_distributes_entries() -> None:
    index = HashIndex(2, fake_hash, FakeOverflow)
    index.build([Page(7, ["a", "bb", "ccc"])])

    assert index.nb == 2
    assert len(index.buckets) == 2
    assert [bucket.id for bucket in index.buckets] == [0, 1]
    assert all(bucket.capacity == 2 for bucket in index.buckets)
    assert index.get_bucket(0).entries == [IndexEntry("bb", 7)]
    assert index.get_bucket(1).entries == [IndexEntry("a", 7), IndexEntry("ccc", 7)]
    assert index.bucket_id_for("ccc") == 1
    assert index.get_bucket(1) is index.buckets[1]
    assert index.total_indexed == 3
    assert index.build_time >= 0


def test_build_preserves_order_pages_and_uses_dependencies() -> None:
    calls = []
    blocks = []

    def recording_hash(key: str, nb: int) -> int:
        calls.append((key, nb))
        return 0

    def factory(capacity: int) -> FakeOverflow:
        block = FakeOverflow(capacity)
        blocks.append(block)
        return block

    pages = [Page(4, ["apple", "house"]), Page(9, ["water", "apple"])]
    original_records = [page.records for page in pages]
    index = HashIndex(2, recording_hash, factory)
    index.build(pages)

    assert index.nb == 3
    assert calls == [("apple", 3), ("house", 3), ("water", 3), ("apple", 3)]
    assert index.total_indexed == 4
    assert index.get_bucket(0).entries == [IndexEntry("apple", 4), IndexEntry("house", 4)]
    assert len(blocks) == 1
    assert blocks[0].capacity == 2
    assert index.get_bucket(0).overflow is blocks[0]
    assert blocks[0].entries == [IndexEntry("water", 9), IndexEntry("apple", 9)]
    assert pages == [Page(4, ["apple", "house"]), Page(9, ["water", "apple"])]
    assert all(page.records is records for page, records in zip(pages, original_records))
    assert index.bucket_id_for("new") == 0
    assert calls[-1] == ("new", 3)


def test_build_records_elapsed_time(monkeypatch) -> None:
    times = iter([10.0, 10.25])
    monkeypatch.setattr("app.core.hash_index.perf_counter", lambda: next(times))
    index = HashIndex(2, fake_hash, FakeOverflow)

    index.build([Page(0, ["apple"])])

    assert index.build_time == 0.25


def test_rebuild_replaces_previous_entries_and_metrics() -> None:
    index = HashIndex(1, fake_hash, FakeOverflow)
    pages = [Page(0, ["apple", "house"])]
    index.build(pages)
    old_buckets = index.buckets
    index.build(pages)

    assert index.buckets is not old_buckets
    assert index.total_indexed == 2
    assert sum(len(bucket.entries) for bucket in index.buckets) == 1
    assert index.get_bucket(2).overflow.entries == [IndexEntry("house", 0)]

    index.build([Page(3, ["a"])])
    assert index.nb == 2
    assert index.total_indexed == 1
    assert index.get_bucket(1).entries == [IndexEntry("a", 3)]
    assert all(bucket.overflow is None for bucket in index.buckets)


def test_build_empty_pages_creates_one_empty_bucket() -> None:
    index = HashIndex(2, fake_hash, FakeOverflow)
    index.build([])

    assert index.nb == 1
    assert index.total_indexed == 0
    assert index.get_bucket(0).entries == []
    assert index.bucket_id_for("missing") == 0


@pytest.mark.parametrize("bucket_id", [None, "0", 0.0, True, False])
def test_get_bucket_rejects_invalid_type(bucket_id: object) -> None:
    index = HashIndex(2, fake_hash, FakeOverflow)
    index.build([])
    with pytest.raises(TypeError):
        index.get_bucket(bucket_id)


@pytest.mark.parametrize("bucket_id", [-1, 1])
def test_get_bucket_rejects_out_of_range_id(bucket_id: int) -> None:
    index = HashIndex(2, fake_hash, FakeOverflow)
    index.build([])
    with pytest.raises(ValueError):
        index.get_bucket(bucket_id)


@pytest.mark.parametrize(
    "result, error",
    [(None, TypeError), ("0", TypeError), (0.0, TypeError),
     (True, TypeError), (False, TypeError), (-1, ValueError), (1, ValueError)],
)
def test_rejects_invalid_hash_result_in_build_and_lookup(result, error) -> None:
    index = HashIndex(2, lambda key, nb: result, FakeOverflow)
    with pytest.raises(error):
        index.build([Page(0, ["apple"])])
    assert index.nb == 0
    assert index.buckets == []
    assert index.total_indexed == 0

    index.build([])
    with pytest.raises(error):
        index.bucket_id_for("apple")


@pytest.mark.parametrize("key, error", [(None, TypeError), (True, TypeError),
                                      (1, TypeError), ("", ValueError), ("   ", ValueError)])
def test_bucket_id_for_rejects_invalid_key(key, error) -> None:
    index = HashIndex(2, fake_hash, FakeOverflow)
    index.build([])
    with pytest.raises(error):
        index.bucket_id_for(key)


def test_failed_rebuild_preserves_previous_index() -> None:
    def failing_hash(key: str, nb: int) -> int:
        if key == "invalid":
            return nb
        return 0

    index = HashIndex(2, failing_hash, FakeOverflow)
    index.build([Page(0, ["apple"])])
    old_buckets = index.buckets
    old_time = index.build_time

    with pytest.raises(ValueError):
        index.build([Page(1, ["house", "invalid"])])

    assert index.buckets is old_buckets
    assert index.nb == 1
    assert index.total_indexed == 1
    assert index.build_time == old_time
    assert index.get_bucket(0).find("apple") == IndexEntry("apple", 0)


def test_search_integration_with_real_index_and_pages() -> None:
    pages = PageManager(["apple", "house", "water"], 2)
    index = HashIndex(1, lambda key, nb: 0, FakeOverflow)
    index.build(pages.pages)

    for key, page_id in [("apple", 0), ("house", 0), ("water", 1)]:
        result = search_by_index(key, index, pages)
        assert result.found is True
        assert result.page_id == page_id
        assert result.bucket_id == 0
        assert result.pages_read == 1

    missing = search_by_index("missing", index, pages)
    assert missing.found is False
    assert missing.pages_read == 0

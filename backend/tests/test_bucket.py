from dataclasses import FrozenInstanceError

import pytest

from app.core.bucket import Bucket, IndexEntry


def test_creates_valid_index_entry() -> None:
    entry = IndexEntry("apple", 0)

    assert entry.key == "apple"
    assert entry.page_id == 0


def test_preserves_original_key_and_page_id() -> None:
    entry = IndexEntry("  Ápple  ", 7)

    assert entry.key == "  Ápple  "
    assert entry.page_id == 7


def test_index_entry_is_immutable() -> None:
    entry = IndexEntry("apple", 0)

    with pytest.raises(FrozenInstanceError):
        entry.key = "house"
    with pytest.raises(FrozenInstanceError):
        entry.page_id = 1

    assert entry.key == "apple"
    assert entry.page_id == 0


@pytest.mark.parametrize("key", ["", "   ", "\t\n"])
def test_rejects_blank_key(key: str) -> None:
    with pytest.raises(ValueError):
        IndexEntry(key, 0)


@pytest.mark.parametrize("key", [None, 123, True])
def test_rejects_invalid_key_type(key: object) -> None:
    with pytest.raises(TypeError):
        IndexEntry(key, 0)


def test_rejects_negative_page_id() -> None:
    with pytest.raises(ValueError):
        IndexEntry("apple", -1)


@pytest.mark.parametrize("page_id", [None, "0", 1.0])
def test_rejects_invalid_page_id_type(page_id: object) -> None:
    with pytest.raises(TypeError):
        IndexEntry("apple", page_id)


@pytest.mark.parametrize("page_id", [True, False])
def test_rejects_boolean_page_id(page_id: bool) -> None:
    with pytest.raises(TypeError):
        IndexEntry("apple", page_id)


class FakeOverflow:
    def __init__(self, capacity: int) -> None:
        self.capacity = capacity
        self.entries: list[IndexEntry] = []
        self.next = None

    def add(self, entry: IndexEntry) -> None:
        self.entries.append(entry)


def test_bucket_starts_empty() -> None:
    bucket = Bucket(0, 2, FakeOverflow)

    assert bucket.id == 0
    assert bucket.capacity == 2
    assert bucket.entries == []
    assert bucket.overflow is None
    assert bucket.is_full() is False
    assert bucket.find("missing") is None


def test_bucket_creates_overflow_only_after_reaching_capacity() -> None:
    created = []

    def factory(capacity: int) -> FakeOverflow:
        block = FakeOverflow(capacity)
        created.append(block)
        return block

    bucket = Bucket(0, 2, factory)
    apple = IndexEntry("apple", 0)
    house = IndexEntry("house", 0)
    water = IndexEntry("water", 0)
    tree = IndexEntry("tree", 1)

    bucket.add(apple)
    assert bucket.is_full() is False
    bucket.add(house)
    assert bucket.is_full() is True
    assert bucket.entries == [apple, house]
    assert bucket.overflow is None
    assert created == []

    bucket.add(water)
    bucket.add(tree)
    assert len(created) == 1
    assert bucket.overflow is created[0]
    assert created[0].capacity == 2
    assert created[0].entries == [water, tree]
    assert bucket.entries == [apple, house]
    assert bucket.find("apple") is apple
    assert bucket.find("house") is house
    assert bucket.find("water") is water
    assert bucket.find("missing") is None


def test_bucket_searches_later_overflow_blocks() -> None:
    bucket = Bucket(0, 1, FakeOverflow)
    bucket.add(IndexEntry("apple", 0))
    bucket.add(IndexEntry("house", 0))
    later_block = FakeOverflow(1)
    water = IndexEntry("water", 1)
    later_block.add(water)
    bucket.overflow.next = later_block

    assert bucket.find("water") is water
    assert bucket.find("missing") is None


def test_bucket_prefers_primary_entry_for_duplicate_key() -> None:
    bucket = Bucket(0, 1, FakeOverflow)
    first = IndexEntry("apple", 0)
    bucket.add(first)
    bucket.add(IndexEntry("apple", 1))

    assert bucket.find("apple") is first


def test_bucket_preserves_search_key() -> None:
    bucket = Bucket(0, 1, FakeOverflow)
    entry = IndexEntry(" Apple ", 0)
    bucket.add(entry)

    assert bucket.find(" Apple ") is entry
    assert bucket.find("Apple") is None
    assert bucket.find(" apple ") is None


def test_buckets_have_independent_storage() -> None:
    first = Bucket(0, 1, FakeOverflow)
    second = Bucket(1, 1, FakeOverflow)
    first.add(IndexEntry("apple", 0))
    first.add(IndexEntry("house", 0))

    assert first.entries is not second.entries
    assert second.entries == []
    assert second.overflow is None


@pytest.mark.parametrize("id", [None, "0", 0.0, True, False])
def test_bucket_rejects_invalid_id_type(id: object) -> None:
    with pytest.raises(TypeError):
        Bucket(id, 2, FakeOverflow)


def test_bucket_rejects_negative_id() -> None:
    with pytest.raises(ValueError):
        Bucket(-1, 2, FakeOverflow)


@pytest.mark.parametrize("capacity", [None, "2", 2.0, True, False])
def test_bucket_rejects_invalid_capacity_type(capacity: object) -> None:
    with pytest.raises(TypeError):
        Bucket(0, capacity, FakeOverflow)


@pytest.mark.parametrize("capacity", [0, -1])
def test_bucket_rejects_non_positive_capacity(capacity: int) -> None:
    with pytest.raises(ValueError):
        Bucket(0, capacity, FakeOverflow)


def test_bucket_rejects_invalid_factory() -> None:
    with pytest.raises(TypeError):
        Bucket(0, 2, None)


@pytest.mark.parametrize("entry", [None, "apple", 1, True])
def test_bucket_rejects_invalid_entry(entry: object) -> None:
    bucket = Bucket(0, 1, FakeOverflow)

    with pytest.raises(TypeError):
        bucket.add(entry)
    assert bucket.entries == []
    assert bucket.overflow is None


@pytest.mark.parametrize("key", [None, 1, True])
def test_bucket_rejects_invalid_search_key_type(key: object) -> None:
    with pytest.raises(TypeError):
        Bucket(0, 1, FakeOverflow).find(key)


@pytest.mark.parametrize("key", ["", "   ", "\t\n"])
def test_bucket_rejects_blank_search_key(key: str) -> None:
    with pytest.raises(ValueError):
        Bucket(0, 1, FakeOverflow).find(key)

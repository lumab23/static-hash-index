from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from app.core.bucket import IndexEntry
from app.core.hash_index import HashIndex
from app.core.index_state import get_current_index, set_current_index
from app.core.pages import Page
from app.main import app


client = TestClient(app)


@pytest.fixture(autouse=True)
def restore_index():
    previous = get_current_index()
    set_current_index(None)
    yield
    set_current_index(previous)


class FakeOverflow:
    def __init__(self, capacity: int) -> None:
        self.entries: list[IndexEntry] = []
        self.next = None

    def add(self, entry: IndexEntry) -> None:
        self.entries.append(entry)


def make_index(words: list[str]) -> HashIndex:
    index = HashIndex(2, lambda key, nb: 0, FakeOverflow)
    index.build([Page(3, words)])
    set_current_index(index)
    return index


def test_bucket_requires_index() -> None:
    response = client.get("/api/index/buckets/0")
    assert response.status_code == 409
    assert response.json() == {"detail": "O índice ainda não foi construído."}


def test_bucket_requires_built_index() -> None:
    set_current_index(HashIndex(2, lambda key, nb: 0, FakeOverflow))
    response = client.get("/api/index/buckets/0")
    assert response.status_code == 409
    assert response.json() == {"detail": "O índice ainda não foi construído."}


@pytest.mark.parametrize("bucket_id", [-1, 2, 999])
def test_missing_bucket_returns_404(bucket_id: int) -> None:
    make_index(["apple", "house"])
    response = client.get(f"/api/index/buckets/{bucket_id}")
    assert response.status_code == 404
    assert response.json() == {"detail": f"Bucket {bucket_id} não encontrado."}


def test_non_integer_id_returns_422() -> None:
    make_index([])
    assert client.get("/api/index/buckets/abc").status_code == 422


def test_empty_bucket() -> None:
    make_index(["apple", "house"])
    response = client.get("/api/index/buckets/1")
    assert response.status_code == 200
    assert response.json() == {
        "id": 1, "capacity": 2, "primary_count": 0, "primary_entries": [],
        "has_overflow": False, "overflow_blocks": [], "total_entries": 0,
    }


def test_primary_entries_preserve_keys_and_order() -> None:
    make_index([" Ápple ", "house"])
    response = client.get("/api/index/buckets/0")
    assert response.status_code == 200
    assert response.json() == {
        "id": 0, "capacity": 2, "primary_count": 2,
        "primary_entries": [{"key": " Ápple ", "page_id": 3},
                            {"key": "house", "page_id": 3}],
        "has_overflow": False, "overflow_blocks": [], "total_entries": 2,
    }


def test_one_overflow_block() -> None:
    make_index(["apple", "house", "water"])
    response = client.get("/api/index/buckets/0")
    assert response.status_code == 200
    body = response.json()
    assert body["primary_count"] == 2
    assert len(body["primary_entries"]) == 2
    assert body["has_overflow"] is True
    assert body["overflow_blocks"] == [
        {"block": 1, "count": 1, "entries": [{"key": "water", "page_id": 3}]}
    ]
    assert body["total_entries"] == 3


def test_multiple_blocks_and_read_only_query(monkeypatch) -> None:
    index = make_index(["apple", "house", " Water "])
    bucket = index.get_bucket(0)
    first = bucket.overflow
    second = FakeOverflow(2)
    second.entries = [IndexEntry("river", 8), IndexEntry("Água", 9)]
    first.next = second
    buckets = index.buckets
    primary = bucket.entries
    first_entries = first.entries
    second_entries = second.entries
    snapshot = deepcopy((primary, first.entries, second.entries))
    metrics = (index.nb, index.bucket_capacity, index.total_indexed, index.build_time)
    requested_ids = []
    original_get_bucket = index.get_bucket

    def get_bucket(bucket_id):
        requested_ids.append(bucket_id)
        return original_get_bucket(bucket_id)

    def unexpected_write(*args):
        raise AssertionError("A consulta não deve construir ou inserir entradas.")

    monkeypatch.setattr(index, "get_bucket", get_bucket)
    monkeypatch.setattr(index, "build", unexpected_write)
    monkeypatch.setattr(bucket, "add", unexpected_write)
    monkeypatch.setattr(first, "add", unexpected_write)
    monkeypatch.setattr(second, "add", unexpected_write)

    response = client.get("/api/index/buckets/0")
    assert response.status_code == 200
    body = response.json()
    assert body["overflow_blocks"] == [
        {"block": 1, "count": 1, "entries": [{"key": " Water ", "page_id": 3}]},
        {"block": 2, "count": 2, "entries": [
            {"key": "river", "page_id": 8}, {"key": "Água", "page_id": 9}]},
    ]
    assert body["total_entries"] == 5
    assert requested_ids == [0]
    assert get_current_index() is index
    assert index.buckets is buckets
    assert bucket.entries is primary
    assert bucket.overflow is first
    assert first.next is second
    assert second.next is None
    assert first.entries is first_entries
    assert second.entries is second_entries
    assert (primary, first.entries, second.entries) == snapshot
    assert (index.nb, index.bucket_capacity, index.total_indexed, index.build_time) == metrics

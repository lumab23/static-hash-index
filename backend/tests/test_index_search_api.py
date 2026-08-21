from dataclasses import dataclass

import pytest
from fastapi.testclient import TestClient

from app.api.routes.index_search import set_hash_index
from app.main import app


client = TestClient(app)


@dataclass
class FakeEntry:
    key: str
    page_id: int


class FakeBucket:
    def __init__(self, entries: list[FakeEntry]) -> None:
        self.entries = entries

    def find(self, key: str) -> FakeEntry | None:
        for entry in self.entries:
            if entry.key == key:
                return entry
        return None


class FakeIndex:
    def __init__(self) -> None:
        self.bucket = FakeBucket([FakeEntry("beta", 0)])

    def bucket_id_for(self, key: str) -> int:
        return 3

    def get_bucket(self, bucket_id: int) -> FakeBucket:
        return self.bucket


@pytest.fixture(autouse=True)
def reset_index() -> None:
    set_hash_index(None)


def load_pages() -> None:
    response = client.post(
        "/api/data/load",
        files={"file": ("words.txt", b"alpha\nbeta\n", "text/plain")},
        data={"page_size": "2"},
    )
    assert response.status_code == 200


def test_search_endpoint_returns_indexed_result() -> None:
    load_pages()
    set_hash_index(FakeIndex())

    response = client.post("/api/search/index", json={"key": "beta"})
    body = response.json()

    assert response.status_code == 200
    assert body["found"] is True
    assert body["key"] == "beta"
    assert body["bucket_id"] == 3
    assert body["page_id"] == 0
    assert body["pages_read"] == 1
    assert body["elapsed_time"] >= 0


def test_search_endpoint_requires_built_index() -> None:
    load_pages()

    response = client.post("/api/search/index", json={"key": "beta"})

    assert response.status_code == 409
    assert response.json() == {"detail": "O índice ainda não foi construído."}


def test_search_endpoint_rejects_empty_key() -> None:
    response = client.post("/api/search/index", json={"key": "  "})

    assert response.status_code == 422

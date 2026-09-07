import pytest
from fastapi.testclient import TestClient

from app.api.routes import data
from app.core.hash_function import hash_key
from app.core.hash_index import HashIndex
from app.core.index_state import get_current_index, set_current_index
from app.core.overflow import OverflowBlock
from app.main import app


client = TestClient(app)


@pytest.fixture(autouse=True)
def restore_state():
    previous_pages = data._page_manager
    previous_index = get_current_index()
    data._page_manager = None
    set_current_index(None)
    yield
    data._page_manager = previous_pages
    set_current_index(previous_index)


def load_data(content: bytes = b"a\ne\ni\n") -> None:
    response = client.post(
        "/api/data/load",
        files={"file": ("words.txt", content, "text/plain")},
        data={"page_size": "1"},
    )
    assert response.status_code == 200


def test_build_requires_loaded_data() -> None:
    response = client.post("/api/index/build", json={"fr": 1})
    assert response.status_code == 409
    assert response.json() == {"detail": "Nenhum arquivo foi carregado."}
    assert get_current_index() is None


@pytest.mark.parametrize("fr", [0, -1, True, False, 1.0, 1.5, "1", None])
def test_build_rejects_invalid_fr(fr) -> None:
    load_data()
    response = client.post("/api/index/build", json={"fr": fr})
    assert response.status_code == 422
    assert get_current_index() is None


def test_build_requires_fr() -> None:
    load_data()
    assert client.post("/api/index/build", json={}).status_code == 422


def test_build_uses_real_dependencies_and_enables_queries() -> None:
    load_data()
    response = client.post("/api/index/build", json={"fr": 1})
    assert response.status_code == 200
    index = get_current_index()
    assert isinstance(index, HashIndex)
    assert response.json() == {
        "fr": 1, "nb": 4, "total_indexed": 3, "build_time": index.build_time,
    }
    assert index.build_time >= 0
    assert index._hash_function is hash_key
    assert index._overflow_factory is OverflowBlock
    assert isinstance(index.get_bucket(1).overflow, OverflowBlock)
    assert client.get("/api/index/summary").json() == response.json()
    bucket = client.get("/api/index/buckets/1")
    assert bucket.status_code == 200
    assert bucket.json()["total_entries"] == 3
    assert len(bucket.json()["overflow_blocks"]) == 2
    result = client.post("/api/search/index", json={"key": "i"})
    assert result.status_code == 200
    assert result.json()["found"] is True
    assert result.json()["page_id"] == 2


def test_rebuild_with_new_fr_replaces_index() -> None:
    load_data()
    client.post("/api/index/build", json={"fr": 1})
    previous = get_current_index()
    response = client.post("/api/index/build", json={"fr": 2})
    assert response.status_code == 200
    assert response.json()["fr"] == 2
    assert response.json()["nb"] == 2
    assert response.json()["total_indexed"] == 3
    assert get_current_index() is not previous


def test_new_upload_invalidates_index() -> None:
    load_data()
    client.post("/api/index/build", json={"fr": 1})
    load_data(b"new\n")
    assert get_current_index() is None
    assert client.get("/api/index/summary").status_code == 409
    assert client.get("/api/index/buckets/0").status_code == 409
    assert client.post("/api/search/index", json={"key": "new"}).status_code == 409


def test_failed_rebuild_preserves_previous_index(monkeypatch) -> None:
    load_data()
    client.post("/api/index/build", json={"fr": 1})
    previous = get_current_index()
    summary = client.get("/api/index/summary").json()

    def fail_build(self, pages):
        raise RuntimeError("Falha simulada na construção.")

    monkeypatch.setattr(HashIndex, "build", fail_build)
    with TestClient(app, raise_server_exceptions=False) as failure_client:
        response = failure_client.post("/api/index/build", json={"fr": 2})
    assert response.status_code == 500
    assert get_current_index() is previous
    assert client.get("/api/index/summary").json() == summary
    assert client.post("/api/search/index", json={"key": "i"}).json()["found"] is True

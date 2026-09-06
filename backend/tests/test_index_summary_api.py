import pytest
from fastapi.testclient import TestClient

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


def unused_overflow_factory(capacity):
    raise AssertionError("Este teste não deve precisar de overflow.")


def test_summary_returns_stored_values_without_building(monkeypatch) -> None:
    index = HashIndex(2, lambda key, nb: 0, unused_overflow_factory)
    index.build([Page(0, ["apple", "house"])])
    set_current_index(index)
    buckets = index.buckets
    expected_time = index.build_time

    def unexpected_build(pages):
        raise AssertionError("Consultar o resumo não deve construir o índice.")

    monkeypatch.setattr(index, "build", unexpected_build)
    response = client.get("/api/index/summary")

    assert response.status_code == 200
    assert response.json() == {
        "fr": 2,
        "nb": 2,
        "total_indexed": 2,
        "build_time": expected_time,
    }
    assert index.buckets is buckets


def test_summary_requires_index() -> None:
    response = client.get("/api/index/summary")

    assert response.status_code == 409
    assert response.json() == {"detail": "O índice ainda não foi construído."}


def test_summary_rejects_unbuilt_index() -> None:
    set_current_index(HashIndex(2, lambda key, nb: 0, unused_overflow_factory))

    response = client.get("/api/index/summary")

    assert response.status_code == 409
    assert response.json() == {"detail": "O índice ainda não foi construído."}

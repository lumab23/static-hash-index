import pytest
from fastapi.testclient import TestClient

from app.api.routes import data
from app.core.index_state import set_current_index
from app.core.metrics import TableScanResult, compare_search_methods, execute_table_scan
from app.core.pages import Page
from app.main import app

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_search_state():
    """
    Limpa páginas e índice para que os testes não compartilhem estado.
    """
    data._page_manager = None
    set_current_index(None)
    yield
    data._page_manager = None
    set_current_index(None)


# --- TESTES UNITÁRIOS (Métricas Core) ---

def test_table_scan_finds_record() -> None:
    pages = [
        Page(0, ["banana", "maca"]),
        Page(1, ["uva", "laranja"]),
        Page(2, ["abacaxi", "morango"])
    ]
    
    result = execute_table_scan(pages, "laranja")
    
    assert result.found is True
    assert result.page_id == 1
    assert result.pages_read == 2 
    assert result.elapsed_time >= 0
    assert "ENCONTRADA na página 1" in result.trace


def test_table_scan_not_found() -> None:
    pages = [
        Page(0, ["banana", "maca"]),
        Page(1, ["uva", "laranja"])
    ]
    
    result = execute_table_scan(pages, "melancia")
    
    assert result.found is False
    assert result.page_id is None
    assert result.pages_read == 2 
    assert "NÃO ENCONTRADA" in result.trace


def test_comparison_calculates_cost_and_percentages() -> None:
    scan_result = TableScanResult(
        found=True,
        key="laranja",
        page_id=3,
        pages_read=4,
        elapsed_time=0.008,
        trace="resultado",
    )

    comparison = compare_search_methods(
        scan_result,
        {
            "found": True,
            "key": "laranja",
            "bucket_id": 2,
            "page_id": 3,
            "pages_read": 1,
            "elapsed_time": 0.002,
            "trace": [],
        },
    )

    assert comparison.results_agree is True
    assert comparison.pages_saved == 3
    assert comparison.page_savings_percentage == 75.0
    assert comparison.time_difference_seconds == 0.006
    assert comparison.time_savings_percentage == 75.0
    assert comparison.speedup_factor == 4.0


# --- TESTES DE API (Integração) ---

def load_pages() -> None:
    """Função auxiliar para carregar dados na memória antes de testar a busca"""
    response = client.post(
        "/api/data/load",
        files={"file": ("words.txt", b"algoritmo\nbanco\ndados\nhash\n", "text/plain")},
        data={"page_size": "2"},
    )
    assert response.status_code == 200


def test_scan_api_success() -> None:
    load_pages()

    response = client.post("/api/search/scan", json={"key": "dados"})
    
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["found"] is True
    assert response_data["page_id"] == 1
    assert response_data["pages_read"] == 2


def test_scan_api_no_pages() -> None:
    # Como a fixture @pytest.fixture(autouse=True) limpou a memória, 
    # não precisamos recriar o client, apenas fazer a requisição.
    response = client.post("/api/search/scan", json={"key": "dados"})
    
    assert response.status_code == 409
    assert "Nenhum arquivo foi carregado." in response.json()["detail"]


def test_scan_api_rejects_blank_key() -> None:
    load_pages()

    response = client.post("/api/search/scan", json={"key": "   "})

    assert response.status_code == 422


def test_compare_api_uses_real_index_and_scan() -> None:
    load_pages()
    assert client.post("/api/index/build", json={"fr": 1}).status_code == 200

    response = client.post("/api/search/compare", json={"key": "dados"})
    body = response.json()

    assert response.status_code == 200
    assert body["results_agree"] is True
    assert body["index_search"]["found"] is True
    assert body["table_scan"]["found"] is True
    assert body["index_search"]["page_id"] == body["table_scan"]["page_id"] == 1
    assert body["index_search"]["pages_read"] == 1
    assert body["table_scan"]["pages_read"] == 2
    assert body["pages_saved"] == 1
    assert body["page_savings_percentage"] == 50.0


def test_compare_api_requires_built_index() -> None:
    load_pages()

    response = client.post("/api/search/compare", json={"key": "dados"})

    assert response.status_code == 409


def test_compare_api_reports_missing_key_in_both_methods() -> None:
    load_pages()
    assert client.post("/api/index/build", json={"fr": 1}).status_code == 200

    response = client.post("/api/search/compare", json={"key": "inexistente"})
    body = response.json()

    assert response.status_code == 200
    assert body["results_agree"] is True
    assert body["index_search"]["found"] is False
    assert body["table_scan"]["found"] is False
    assert body["table_scan"]["pages_read"] == 2

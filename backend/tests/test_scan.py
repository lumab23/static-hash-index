import pytest
from fastapi.testclient import TestClient

from app.api.routes import data
from app.core.metrics import execute_table_scan
from app.core.pages import Page
from app.main import app

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_page_manager() -> None:
    """
    Fixture que roda automaticamente antes de cada teste.
    Garante que a memória (estado global em data.py) seja limpa,
    evitando que um teste suje o resultado do outro.
    """
    data._page_manager = None


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
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_load_data_and_get_summary() -> None:
    response = client.post(
        "/api/data/load",
        files={"file": ("words.txt", b"alpha\nbeta\ngamma\n", "text/plain")},
        data={"page_size": "2"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "total_records": 3,
        "total_pages": 2,
        "page_size": 2,
        "first_page": {"id": 0, "records": ["alpha", "beta"]},
        "last_page": {"id": 1, "records": ["gamma"]},
    }
    assert client.get("/api/pages/summary").json() == response.json()


def test_load_data_rejects_invalid_page_size() -> None:
    response = client.post(
        "/api/data/load",
        files={"file": ("words.txt", b"alpha\n", "text/plain")},
        data={"page_size": "0"},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "O tamanho da página deve ser maior que zero."}


def test_load_data_rejects_non_txt_file() -> None:
    response = client.post(
        "/api/data/load",
        files={"file": ("words.csv", b"alpha\n", "text/csv")},
        data={"page_size": "1"},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Envie um arquivo com extensão .txt."}

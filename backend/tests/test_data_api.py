import asyncio

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.api.routes import data
from app.core.index_state import set_current_index
from app.main import app


client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_data_state():
    data._page_manager = None
    data._upload_generation = 0
    set_current_index(None)
    yield
    data._page_manager = None
    data._upload_generation = 0
    set_current_index(None)


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


def test_get_page_by_id() -> None:
    client.post(
        "/api/data/load",
        files={"file": ("words.txt", b"alpha\nbeta\ngamma\n", "text/plain")},
        data={"page_size": "2"},
    )

    response = client.get("/api/pages/1")

    assert response.status_code == 200
    assert response.json() == {"id": 1, "records": ["gamma"]}


def test_get_unknown_page_returns_not_found() -> None:
    client.post(
        "/api/data/load",
        files={"file": ("words.txt", b"alpha\n", "text/plain")},
        data={"page_size": "1"},
    )

    response = client.get("/api/pages/4")

    assert response.status_code == 404


def test_get_page_records_returns_only_requested_slice() -> None:
    content = "\n".join(f"word-{position:03d}" for position in range(250)).encode()
    client.post(
        "/api/data/load",
        files={"file": ("words.txt", content, "text/plain")},
        data={"page_size": "250"},
    )

    response = client.get("/api/pages/0/records", params={"offset": 100, "limit": 100})

    assert response.status_code == 200
    assert response.json() == {
        "id": 0,
        "total_records": 250,
        "offset": 100,
        "limit": 100,
        "records": [f"word-{position:03d}" for position in range(100, 200)],
        "has_previous": True,
        "has_next": True,
    }


@pytest.mark.parametrize(
    ("params", "status_code"),
    [
        ({"offset": -1}, 422),
        ({"limit": 0}, 422),
        ({"limit": 101}, 422),
        ({"offset": 251}, 400),
    ],
)
def test_get_page_records_validates_window(params: dict, status_code: int) -> None:
    content = "\n".join(f"word-{position:03d}" for position in range(250)).encode()
    client.post(
        "/api/data/load",
        files={"file": ("words.txt", content, "text/plain")},
        data={"page_size": "250"},
    )

    response = client.get("/api/pages/0/records", params=params)

    assert response.status_code == status_code


def test_page_records_requires_loaded_data() -> None:
    response = client.get("/api/pages/0/records")

    assert response.status_code == 409


class ControlledUpload:
    def __init__(
        self,
        filename: str,
        content: bytes,
        started: asyncio.Event,
        release: asyncio.Event,
    ) -> None:
        self.filename = filename
        self._content = content
        self._started = started
        self._release = release

    async def read(self) -> bytes:
        self._started.set()
        await self._release.wait()
        return self._content


def test_late_upload_cannot_replace_newer_dataset() -> None:
    async def exercise_race() -> None:
        old_started = asyncio.Event()
        release_old = asyncio.Event()
        new_started = asyncio.Event()
        release_new = asyncio.Event()
        release_new.set()

        old_upload = ControlledUpload(
            "old.txt", b"old-1\nold-2\n", old_started, release_old
        )
        new_upload = ControlledUpload("new.txt", b"new-1\n", new_started, release_new)

        old_task = asyncio.create_task(data.load_data(file=old_upload, page_size=1))
        await old_started.wait()
        newest_summary = await data.load_data(file=new_upload, page_size=1)
        release_old.set()

        with pytest.raises(HTTPException) as error:
            await old_task

        assert error.value.status_code == 409
        assert newest_summary["total_records"] == 1
        assert data.get_page_manager().records == ["new-1"]

    asyncio.run(exercise_race())

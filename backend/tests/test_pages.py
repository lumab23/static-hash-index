import pytest

from app.core.pages import DataValidationError, PageManager, load_words


def test_divides_records_into_zero_based_pages() -> None:
    manager = PageManager(["alpha", "beta", "gamma", "delta", "epsilon"], 2)

    assert manager.total_records == 5
    assert manager.total_pages == 3
    assert manager.pages[0].id == 0
    assert manager.pages[0].records == ["alpha", "beta"]
    assert manager.pages[-1].id == 2
    assert manager.pages[-1].records == ["epsilon"]


def test_summary_exposes_first_and_last_page() -> None:
    summary = PageManager(["alpha", "beta", "gamma"], 2).summary()

    assert summary == {
        "total_records": 3,
        "total_pages": 2,
        "page_size": 2,
        "first_page": {"id": 0, "records": ["alpha", "beta"]},
        "last_page": {"id": 1, "records": ["gamma"]},
    }


def test_summary_shows_only_first_five_records_from_each_page() -> None:
    records = [f"word-{number}" for number in range(14)]

    summary = PageManager(records, 7).summary()

    assert summary["first_page"]["records"] == records[:5]
    assert summary["last_page"]["records"] == records[7:12]


@pytest.mark.parametrize("page_size", [0, -1])
def test_rejects_invalid_page_size(page_size: int) -> None:
    with pytest.raises(DataValidationError):
        PageManager(["alpha"], page_size)


def test_rejects_empty_records() -> None:
    with pytest.raises(DataValidationError, match="ao menos um registro"):
        PageManager([], 2)


def test_load_words_accepts_utf8_bom_and_ignores_blank_lines() -> None:
    assert load_words("\ufeffalpha\n\nbeta\r\n".encode()) == ["alpha", "beta"]


@pytest.mark.parametrize("content", [b"", b"\n  \r\n"])
def test_load_words_rejects_empty_file(content: bytes) -> None:
    with pytest.raises(DataValidationError):
        load_words(content)


def test_load_words_rejects_non_utf8_file() -> None:
    with pytest.raises(DataValidationError, match="UTF-8"):
        load_words(b"\xff\xfe")


@pytest.mark.parametrize("page_id", [-1, 4])
def test_get_page_rejects_unknown_page(page_id: int) -> None:
    manager = PageManager(["alpha"], 1)

    with pytest.raises(DataValidationError, match="não encontrada"):
        manager.get_page(page_id)

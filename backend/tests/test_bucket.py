from dataclasses import FrozenInstanceError

import pytest

from app.core.bucket import IndexEntry


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

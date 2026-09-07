import pytest

from app.core.overflow import OverflowBlock


def test_criar_overflow():
    overflow = OverflowBlock(2)

    assert overflow.capacity == 2
    assert overflow.entries == []
    assert overflow.next is None


def test_adicionar_entries():
    overflow = OverflowBlock(2)

    overflow.add("banana")
    overflow.add("uva")

    assert overflow.entries == ["banana", "uva"]


def test_criar_novo_bloco_quando_cheio():
    overflow = OverflowBlock(2)

    overflow.add("banana")
    overflow.add("uva")
    overflow.add("abacaxi")

    assert overflow.entries == ["banana", "uva"]
    assert overflow.next is not None
    assert overflow.next.entries == ["abacaxi"]


def test_multiplos_blocos_overflow():
    overflow = OverflowBlock(2)

    overflow.add("banana")
    overflow.add("uva")
    overflow.add("abacaxi")
    overflow.add("morango")
    overflow.add("laranja")

    assert overflow.get_all_entries() == [
        "banana",
        "uva",
        "abacaxi",
        "morango",
        "laranja",
    ]


def test_capacidade_invalida():
    with pytest.raises(ValueError):
        OverflowBlock(0)
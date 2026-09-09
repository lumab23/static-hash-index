import pytest

from app.core.hash_function import hash_key


def test_hash_deterministico():
    resultado_1 = hash_key("banana", 10)
    resultado_2 = hash_key("banana", 10)

    assert resultado_1 == resultado_2


def test_hash_dentro_do_intervalo():
    nb = 10

    for chave in ["banana", "abacaxi", "uva", "morango", "laranja"]:
        resultado = hash_key(chave, nb)

        assert 0 <= resultado < nb


def test_hash_nb_invalido():
    with pytest.raises(ValueError):
        hash_key("banana", 0)


def test_hash_chaves_diferentes():
    resultado_1 = hash_key("banana", 10)
    resultado_2 = hash_key("abacaxi", 10)

    assert isinstance(resultado_1, int)
    assert isinstance(resultado_2, int)
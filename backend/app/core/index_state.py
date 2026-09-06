from app.core.search import SearchIndex


_current_index: SearchIndex | None = None


def set_current_index(index: SearchIndex | None) -> None:
    """Registra o índice disponível para as rotas de busca."""
    global _current_index
    _current_index = index


def get_current_index() -> SearchIndex | None:
    """Retorna o índice atual, caso ele já tenha sido construído."""
    return _current_index

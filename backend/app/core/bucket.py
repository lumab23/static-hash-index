from dataclasses import dataclass


@dataclass(frozen=True)
class IndexEntry:
    key: str
    page_id: int

    def __post_init__(self) -> None:
        if not isinstance(self.key, str):
            raise TypeError("A chave deve ser uma string.")
        if not self.key.strip():
            raise ValueError("A chave não pode estar vazia ou conter apenas espaços.")

        if isinstance(self.page_id, bool) or not isinstance(self.page_id, int):
            raise TypeError("O identificador da página deve ser um inteiro.")
        if self.page_id < 0:
            raise ValueError("O identificador da página deve ser maior ou igual a zero.")

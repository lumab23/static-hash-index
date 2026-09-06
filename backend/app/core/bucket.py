from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol


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


class Overflow(Protocol):
    entries: list[IndexEntry]
    next: Overflow | None

    def add(self, entry: IndexEntry) -> None: ...


class Bucket:
    def __init__(
        self, id: int, capacity: int, overflow_factory: Callable[[int], Overflow]
    ) -> None:
        if isinstance(id, bool) or not isinstance(id, int):
            raise TypeError("O identificador do bucket deve ser um inteiro.")
        if id < 0:
            raise ValueError("O identificador do bucket deve ser maior ou igual a zero.")
        if isinstance(capacity, bool) or not isinstance(capacity, int):
            raise TypeError("A capacidade do bucket deve ser um inteiro.")
        if capacity <= 0:
            raise ValueError("A capacidade do bucket deve ser maior que zero.")
        if not callable(overflow_factory):
            raise TypeError("A fábrica de overflow deve ser chamável.")

        self.id = id
        self.capacity = capacity
        self.entries: list[IndexEntry] = []
        self.overflow: Overflow | None = None
        self._overflow_factory = overflow_factory

    def is_full(self) -> bool:
        return len(self.entries) >= self.capacity

    def add(self, entry: IndexEntry) -> None:
        if not isinstance(entry, IndexEntry):
            raise TypeError("A entrada deve ser um IndexEntry.")

        if not self.is_full():
            self.entries.append(entry)
        else:
            if self.overflow is None:
                self.overflow = self._overflow_factory(self.capacity)
            self.overflow.add(entry)

    def find(self, key: str) -> IndexEntry | None:
        if not isinstance(key, str):
            raise TypeError("A chave deve ser uma string.")
        if not key.strip():
            raise ValueError("A chave não pode estar vazia ou conter apenas espaços.")

        for entry in self.entries:
            if entry.key == key:
                return entry

        block = self.overflow
        while block is not None:
            for entry in block.entries:
                if entry.key == key:
                    return entry
            block = block.next
        return None

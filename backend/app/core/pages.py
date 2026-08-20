from __future__ import annotations

from dataclasses import dataclass


class DataValidationError(ValueError):
    pass


@dataclass
class Page:
    id: int
    records: list[str]

    def to_dict(self) -> dict:
        return {"id": self.id, "records": list(self.records)}


def load_words(content: bytes) -> list[str]:
    if not content:
        raise DataValidationError("O arquivo TXT está vazio.")

    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise DataValidationError("O arquivo deve estar codificado em UTF-8.") from exc

    words = [line.strip() for line in text.splitlines() if line.strip()]
    if not words:
        raise DataValidationError("O arquivo TXT não contém palavras.")

    return words


class PageManager:
    def __init__(self, records: list[str], page_size: int) -> None:
        if page_size <= 0:
            raise DataValidationError("O tamanho da página deve ser maior que zero.")
        if not records:
            raise DataValidationError("É necessário informar ao menos um registro.")

        self.records = records
        self.page_size = page_size
        total_pages = (len(records) + page_size - 1) // page_size
        self.pages = [Page(page_id, []) for page_id in range(total_pages)]

        for position, record in enumerate(records):
            page_id = position // page_size
            self.pages[page_id].records.append(record)

    @classmethod
    def from_txt(cls, content: bytes, page_size: int) -> PageManager:
        return cls(load_words(content), page_size)

    @property
    def total_records(self) -> int:
        return len(self.records)

    @property
    def total_pages(self) -> int:
        return len(self.pages)

    def get_page(self, page_id: int) -> Page:
        if page_id < 0 or page_id >= self.total_pages:
            raise DataValidationError(f"Página {page_id} não encontrada.")
        return self.pages[page_id]

    def summary(self) -> dict:
        return {
            "total_records": self.total_records,
            "total_pages": self.total_pages,
            "page_size": self.page_size,
            "first_page": self._page_preview(self.pages[0]),
            "last_page": self._page_preview(self.pages[-1]),
        }

    def _page_preview(self, page: Page) -> dict:
        return {"id": page.id, "records": page.records[:5]}

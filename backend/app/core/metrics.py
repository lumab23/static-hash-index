import time
from typing import Any

from pydantic import BaseModel, Field

from app.core.pages import Page


class TableScanResult(BaseModel):
    """
    Estrutura que representa o resultado da execução do Table Scan (varredura sequencial).
    """
    found: bool = Field(..., description="Indica se a chave foi encontrada nas páginas.")
    key: str = Field(..., description="A chave pesquisada.")
    page_id: int | None = Field(None, description="ID da página onde o registro foi localizado.")
    pages_read: int = Field(..., description="Total de páginas lidas até encontrar ou finalizar.")
    elapsed_time: float = Field(..., description="Tempo de execução em segundos com alta precisão.")
    trace: str = Field(..., description="Resumo explicativo do caminho percorrido no scan.")


class ComparisonMetrics(BaseModel):
    """
    Estrutura consolidada para comparar a Busca Indexada (Luma) vs Table Scan (Bianca).
    """
    key: str
    table_scan: TableScanResult
    index_search: dict[str, Any]
    results_agree: bool = Field(..., description="As duas estratégias concordam sobre o resultado.")
    pages_saved: int = Field(..., description="Diferença de páginas lidas (Scan - Índice).")
    page_savings_percentage: float = Field(..., description="Percentual de páginas economizadas.")
    time_difference_seconds: float = Field(..., description="Diferença de tempo em segundos.")
    time_savings_percentage: float = Field(..., description="Diferença percentual de tempo.")
    speedup_factor: float = Field(..., description="Quantas vezes a busca indexada foi mais rápida.")


def execute_table_scan(pages: list[Page], key: str) -> TableScanResult:
    """
    Executa a busca sequencial (Table Scan) percorrendo página por página.
    """
    if not isinstance(key, str):
        raise TypeError("A chave deve ser uma string.")
    if not key.strip():
        raise ValueError("A chave não pode estar vazia.")

    start_time = time.perf_counter()
    pages_read = 0
    found = False
    target_page_id = None

    for page in pages:
        pages_read += 1
        if key in page.records:
            found = True
            target_page_id = page.id
            break

    elapsed_time = time.perf_counter() - start_time

    if found:
        trace_msg = f"Chave '{key}' ENCONTRADA na página {target_page_id} após ler {pages_read} página(s)."
    else:
        trace_msg = f"Chave '{key}' NÃO ENCONTRADA após varredura total de {pages_read} página(s)."

    return TableScanResult(
        found=found,
        key=key,
        page_id=target_page_id,
        pages_read=pages_read,
        elapsed_time=elapsed_time,
        trace=trace_msg,
    )


def compare_search_methods(scan_res: TableScanResult, index_res: dict[str, Any]) -> ComparisonMetrics:
    """
    Consolida e calcula a diferença de desempenho entre Table Scan e Busca Indexada.
    """
    index_pages = int(index_res["pages_read"])
    index_time = float(index_res["elapsed_time"])

    pages_saved = max(0, scan_res.pages_read - index_pages)
    page_savings = (
        pages_saved / scan_res.pages_read * 100 if scan_res.pages_read else 0.0
    )
    time_diff = scan_res.elapsed_time - index_time
    time_savings = (
        time_diff / scan_res.elapsed_time * 100 if scan_res.elapsed_time else 0.0
    )
    speedup = scan_res.elapsed_time / index_time if index_time > 0 else 0.0

    return ComparisonMetrics(
        key=scan_res.key,
        table_scan=scan_res,
        index_search=index_res,
        results_agree=scan_res.found == bool(index_res["found"]),
        pages_saved=pages_saved,
        page_savings_percentage=round(page_savings, 2),
        time_difference_seconds=round(time_diff, 6),
        time_savings_percentage=round(time_savings, 2),
        speedup_factor=round(speedup, 2),
    )

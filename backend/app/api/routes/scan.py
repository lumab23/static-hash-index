from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field

from app.api.routes.data import get_page_manager
from app.core.metrics import (
    ComparisonMetrics,
    TableScanResult,
    compare_search_methods,
    execute_table_scan,
)
from app.core.pages import PageManager

router = APIRouter(tags=["search"])


class ScanRequest(BaseModel):
    key: str = Field(..., min_length=1, description="Chave/palavra a ser buscada")


class CompareRequest(BaseModel):
    key: str = Field(..., min_length=1, description="Chave/palavra a ser buscada")
    index_search_result: dict = Field(..., description="Resultado retornado da busca indexada (Luma)")


@router.post("/search/scan", response_model=TableScanResult, status_code=status.HTTP_200_OK)
def run_table_scan(
    payload: ScanRequest,
    page_manager: PageManager = Depends(get_page_manager),
) -> TableScanResult:
    """
    Executa a varredura sequencial (Table Scan) nas páginas em memória.
    """
    return execute_table_scan(page_manager.pages, payload.key)


@router.post("/search/compare", response_model=ComparisonMetrics, status_code=status.HTTP_200_OK)
def run_comparison(
    payload: CompareRequest,
    page_manager: PageManager = Depends(get_page_manager),
) -> ComparisonMetrics:
    """
    Consolida e compara os resultados do Table Scan com a Busca Indexada da Luma.
    """
    scan_result = execute_table_scan(page_manager.pages, payload.key)
    return compare_search_methods(scan_result, payload.index_search_result)
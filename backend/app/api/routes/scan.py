from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, field_validator

from app.api.routes.data import get_page_manager
from app.api.routes.index_search import get_hash_index
from app.core.metrics import (
    ComparisonMetrics,
    TableScanResult,
    compare_search_methods,
    execute_table_scan,
)
from app.core.pages import PageManager
from app.core.search import search_by_index

router = APIRouter(tags=["search"])


class SearchRequest(BaseModel):
    key: str

    @field_validator("key")
    @classmethod
    def validate_key(cls, key: str) -> str:
        key = key.strip()
        if not key:
            raise ValueError("Informe uma chave de busca.")
        return key


class ScanRequest(SearchRequest):
    pass


class CompareRequest(SearchRequest):
    pass


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
    index_result = search_by_index(payload.key, get_hash_index(), page_manager)
    scan_result = execute_table_scan(page_manager.pages, payload.key)
    return compare_search_methods(scan_result, index_result.to_dict())

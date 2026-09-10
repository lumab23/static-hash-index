#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path
from time import perf_counter

from fastapi.testclient import TestClient


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.main import app  # noqa: E402


def require_success(response, operation: str) -> dict:
    if not response.is_success:
        raise RuntimeError(
            f"{operation} falhou com HTTP {response.status_code}: {response.text}"
        )
    return response.json()


def inspect_dataset(path: Path) -> tuple[int, dict[str, str]]:
    count = 0
    first = None
    middle = None
    last = None

    with path.open(encoding="utf-8") as stream:
        for count, line in enumerate(stream, start=1):
            key = line.rstrip("\n\r")
            if count == 1:
                first = key
            last = key

    if count == 0 or first is None or last is None:
        raise ValueError("O arquivo de escala está vazio.")

    middle_position = count // 2
    with path.open(encoding="utf-8") as stream:
        for position, line in enumerate(stream):
            if position == middle_position:
                middle = line.rstrip("\n\r")
                break

    return count, {
        "initial": first,
        "middle": middle,
        "final": last,
        "missing": "word-not-present-in-dataset",
    }


def measured_request(operation):
    started_at = perf_counter()
    response = operation()
    return response, (perf_counter() - started_at) * 1000


def run(dataset: Path, page_size: int, fr: int) -> dict:
    total_records, keys = inspect_dataset(dataset)
    client = TestClient(app)

    with dataset.open("rb") as stream:
        upload_response, upload_ms = measured_request(
            lambda: client.post(
                "/api/data/load",
                files={"file": (dataset.name, stream, "text/plain")},
                data={"page_size": str(page_size)},
            )
        )
    upload_summary = require_success(upload_response, "Upload")
    expected_pages = (total_records + page_size - 1) // page_size
    assert upload_summary["total_records"] == total_records
    assert upload_summary["total_pages"] == expected_pages
    assert len(upload_summary["first_page"]["records"]) <= 5
    assert len(upload_summary["last_page"]["records"]) <= 5

    summary = require_success(client.get("/api/pages/summary"), "Resumo de páginas")
    assert summary == upload_summary
    last_page_id = expected_pages - 1
    page_window = require_success(
        client.get(
            f"/api/pages/{last_page_id}/records",
            params={"offset": 0, "limit": 100},
        ),
        "Consulta paginada",
    )
    assert page_window["id"] == last_page_id
    assert len(page_window["records"]) <= 100
    assert page_window["records"][-1] == keys["final"]

    build_response, build_request_ms = measured_request(
        lambda: client.post("/api/index/build", json={"fr": fr})
    )
    index_summary = require_success(build_response, "Construção do índice")
    assert index_summary["total_indexed"] == total_records
    assert "buckets" not in index_summary

    searches = {}
    for label, key in keys.items():
        response, request_ms = measured_request(
            lambda current_key=key: client.post(
                "/api/search/index", json={"key": current_key}
            )
        )
        result = require_success(response, f"Busca {label}")
        assert result["found"] is (label != "missing")
        searches[label] = {
            "key": key,
            "request_ms": round(request_ms, 4),
            "core_ms": round(result["elapsed_time"] * 1000, 4),
            "page_id": result["page_id"],
            "pages_read": result["pages_read"],
        }

    replacement = require_success(
        client.post(
            "/api/data/load",
            files={"file": ("replacement.txt", b"replacement\n", "text/plain")},
            data={"page_size": "1"},
        ),
        "Novo upload",
    )
    assert replacement["total_records"] == 1
    blocked_search = client.post("/api/search/index", json={"key": "replacement"})
    assert blocked_search.status_code == 409

    return {
        "dataset": str(dataset),
        "total_records": total_records,
        "page_size": page_size,
        "total_pages": expected_pages,
        "fr": fr,
        "nb": index_summary["nb"],
        "measurements_ms": {
            "upload_and_processing": round(upload_ms, 4),
            "index_build_request": round(build_request_ms, 4),
            "index_build_core": round(index_summary["build_time"] * 1000, 4),
            "searches": searches,
        },
        "response_limits": {
            "first_page_preview": len(upload_summary["first_page"]["records"]),
            "last_page_preview": len(upload_summary["last_page"]["records"]),
            "page_window": len(page_window["records"]),
            "index_summary_contains_buckets": False,
        },
        "new_upload_invalidated_index": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Executa o fluxo real de escala pela API.")
    parser.add_argument("dataset", type=Path)
    parser.add_argument("--page-size", type=int, default=100)
    parser.add_argument("--fr", type=int, default=100)
    args = parser.parse_args()

    result = run(args.dataset, args.page_size, args.fr)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

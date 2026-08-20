# Backend

API FastAPI e núcleo Python do índice HASH estático.

## Requisitos

- Python 3.11 ou superior

## Ambiente local

Execute os comandos a partir desta pasta:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e '.[dev]'
uvicorn app.main:app --reload
```

A API ficará disponível em `http://127.0.0.1:8000`. A documentação interativa
estará em `/docs` e o endpoint de diagnóstico em `/api/health`.

## Testes

```bash
pytest
```

## Organização

- `app/api/`: endpoints e contratos HTTP.
- `app/core/`: páginas, índice, buscas e métricas.
- `tests/`: testes automatizados.

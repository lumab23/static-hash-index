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

## Dataset de palavras

O projeto usa a lista pública [dwyl/english-words](https://github.com/dwyl/english-words).
Baixe `words.txt` e salve-o em `data/words.txt` na raiz do projeto. Essa é a lista
com aproximadamente 466 mil registros mencionada no enunciado. O diretório
`data/` é ignorado pelo Git para evitar versionar o dataset externo.

Com a API em execução, carregue o arquivo definindo também o tamanho da página:

```bash
curl -X POST http://127.0.0.1:8000/api/data/load \
  -F 'file=@../data/words.txt' \
  -F 'page_size=100'
```

O resumo corrente pode ser consultado em `GET /api/pages/summary`.

## Testes

```bash
pytest
```

## Organização

- `app/api/`: endpoints e contratos HTTP.
- `app/core/`: páginas, índice, buscas e métricas.
- `tests/`: testes automatizados.

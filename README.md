# Static Hash Index

Monorepo do projeto acadêmico de simulação de um índice HASH estático.

## Aplicações

- `backend/`: API FastAPI e núcleo Python do projeto.
- `frontend/`: aplicação React com Vite e Tailwind CSS.

Cada aplicação mantém suas próprias dependências e instruções. Consulte o
README dentro da pasta correspondente.

## Estrutura

```text
static-hash-index/
├── backend/
│   ├── app/
│   ├── tests/
│   ├── pyproject.toml
│   └── README.md
├── frontend/
│   ├── src/
│   ├── tests/
│   ├── package.json
│   └── README.md
├── .gitignore
└── README.md
```


## Execução local

Em um terminal:

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload
```

Em outro terminal:

```bash
cd frontend
npm run dev
```

Abra `http://127.0.0.1:5173`. O Vite encaminha as chamadas `/api` para o
FastAPI em `http://127.0.0.1:8000`.

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

## Contrato com a construção do índice

Depois de construir um `HashIndex`, a rota de construção deve registrá-lo com
`set_hash_index(index)`, de `app.api.routes.index_search`. A busca depende dos
métodos `bucket_id_for(key)` e `get_bucket(bucket_id)`, e cada bucket deve expor
`find(key)`. O carregamento de um novo TXT invalida automaticamente o índice
anterior para impedir buscas em páginas desatualizadas.

## Testes

```bash
pytest
```

## Organização

- `app/api/`: endpoints e contratos HTTP.
- `app/core/`: páginas, índice, buscas e métricas.
- `tests/`: testes automatizados.

### Visualização de hash e overflow

`GET /api/index/hash-overflow?key=banana` consulta o índice atual, sem inserir
registros ou confirmar a existência da chave. Retorna `key`, `bucket_id`,
`bucket_capacity`, `bucket_occupancy` (entradas na área primária) e
`overflow_entries` (chaves de todos os blocos de overflow desse bucket, em ordem).
A chave é preservada exatamente como recebida; chaves vazias ou apenas com
espaços retornam 422. Sem índice construído, retorna 409.

As métricas são globais e reiniciadas a cada construção:

- `collision_count`: inserções que encontraram a área primária cheia.
- `collision_rate`: `collision_count / total_indexed * 100`, ou zero sem entradas.
- `overflow_bucket_count`: quantidade de buckets primários com overflow,
  independentemente do número de blocos encadeados.
- `overflow_rate`: `overflow_bucket_count / NB * 100`.

O valor de hash exibido é o próprio endereço `bucket_id`, calculado pela
`hash_function.py` existente. No frontend, construa o índice no painel existente
e use “Consultar hash”; uma reconstrução limpa a consulta anterior.

### Table scan e comparação

`POST /api/search/scan` percorre as páginas em ordem e recebe apenas `key`.
`POST /api/search/compare` também recebe somente `key` e executa no backend a
busca indexada e o table scan sobre o mesmo conjunto de páginas. Assim, a
comparação não aceita métricas fornecidas pelo navegador.

As métricas de comparação seguem estas convenções:

- `pages_saved`: páginas lidas pelo scan menos páginas lidas pelo índice, com
  mínimo zero.
- `page_savings_percentage`: `pages_saved / pages_read_scan * 100`.
- `time_difference_seconds`: tempo do scan menos tempo da busca indexada.
- `time_savings_percentage`: diferença de tempo dividida pelo tempo do scan,
  multiplicada por 100; pode ser negativa quando o índice for mais lento.
- `speedup_factor`: tempo do scan dividido pelo tempo da busca indexada.
- `results_agree`: informa se as duas estratégias concordam sobre a existência
  da chave.

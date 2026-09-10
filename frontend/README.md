# Frontend

Interface React do projeto, criada com Vite e Tailwind CSS.

```bash
npm install
npm run dev
```

Para validar a aplicação:

```bash
npm test
npm run lint
npm run build
```

Durante o desenvolvimento, as chamadas `/api` são encaminhadas pelo Vite ao
FastAPI em `http://127.0.0.1:8000`. O fluxo da interface é: carregar TXT,
consultar páginas sob demanda, construir o índice e então habilitar hash, busca
indexada e comparação. Cada consulta de página renderiza no máximo 100 registros.

## Teste completo pela interface

Antes de começar, mantenha o backend e o frontend em execução e abra
`http://127.0.0.1:5173` no navegador.

1. Na etapa **Carregar dados e consultar páginas**, selecione um arquivo `.txt`
   codificado em UTF-8 e com um registro por linha. Para reproduzir o enunciado,
   use `data/words.txt` e informe `100` como tamanho da página.
2. Clique em **Carregar arquivo** e aguarde a confirmação. Confira o total de
   registros, o total de páginas e as prévias da primeira e da última página.
3. Em **Consultar página por ID**, consulte a página `0`, uma página
   intermediária e o ID exibido para a última página. Uma consulta devolve no
   máximo 100 registros. Se a página tiver mais registros, use **Anteriores** e
   **Próximos** para percorrer seus blocos sem carregar tudo de uma vez.
4. Na etapa **Construir e explorar o índice**, informe uma capacidade de bucket
   válida, como `100`, e clique em **Construir índice**. Aguarde o status
   **Índice pronto** e confira FR, NB, total indexado e tempo de construção.
5. Opcionalmente, informe um ID válido em **Detalhes de um bucket** para conferir
   suas entradas primárias e seus blocos adicionais.
6. Em **Busca por índice**, pesquise uma chave existente no TXT e depois uma
   chave inexistente. Confira o bucket calculado, a página, as páginas lidas e o
   caminho da busca.
7. Em **Hash, colisão e overflow**, consulte uma chave para verificar ocupação,
   colisões, taxas e entradas adicionais do bucket correspondente.
8. Em **Comparar métodos de busca**, execute primeiro o **Table Scan** e depois
   **Comparar custos**. Os painéis **Busca indexada** e **Table Scan** devem
   concordar sobre a existência da chave.
9. Carregue outro TXT, ou recarregue o mesmo arquivo. Os resultados anteriores
   devem desaparecer e as buscas indexadas devem permanecer bloqueadas até a
   construção de um novo índice.

Para testar a navegação interna de uma página, carregue o arquivo com tamanho de
página maior que `100`, por exemplo `500`. Ao consultar uma página cheia, o botão
**Próximos** avança para os registros 101–200 e **Anteriores** retorna ao bloco
anterior. Esses botões não alteram o ID da página consultada.

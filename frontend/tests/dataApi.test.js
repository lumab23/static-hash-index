import assert from 'node:assert/strict'
import test from 'node:test'

import { getPageRecords, getPagesSummary, loadData } from '../src/features/data/dataApi.js'

test('envia arquivo e tamanho da página como multipart', async t => {
  t.mock.method(globalThis, 'fetch', async (url, options) => {
    assert.equal(url, '/api/data/load')
    assert.equal(options.method, 'POST')
    assert.equal(options.body.get('page_size'), '100')
    assert.ok(options.body.get('file') instanceof Blob)
    return Response.json({ total_records: 1 })
  })

  const result = await loadData(new Blob(['alpha\n'], { type: 'text/plain' }), 100)

  assert.equal(result.total_records, 1)
})

test('consulta somente uma janela limitada da página', async t => {
  const controller = new AbortController()
  t.mock.method(globalThis, 'fetch', async (url, options) => {
    assert.equal(url, '/api/pages/7/records?offset=100&limit=100')
    assert.equal(options.signal, controller.signal)
    return Response.json({ id: 7, records: [] })
  })

  const result = await getPageRecords(7, 100, 100, controller.signal)

  assert.equal(result.id, 7)
})

test('preserva status e mensagem retornados pela API', async t => {
  t.mock.method(globalThis, 'fetch', async () => Response.json(
    { detail: 'Nenhum arquivo foi carregado.' },
    { status: 409 },
  ))

  await assert.rejects(
    getPagesSummary(),
    error => error.status === 409 && error.message === 'Nenhum arquivo foi carregado.',
  )
})

import assert from 'node:assert/strict'
import test from 'node:test'

import { createLatestRequestRunner } from '../src/features/data/latestRequest.js'

function deferred() {
  let resolve
  const promise = new Promise(done => { resolve = done })
  return { promise, resolve }
}

test('ignora resposta antiga que termina depois da solicitação mais recente', async () => {
  const runner = createLatestRequestRunner()
  const firstResult = deferred()
  const secondResult = deferred()

  const first = runner.run(() => firstResult.promise)
  const second = runner.run(() => secondResult.promise)

  secondResult.resolve('arquivo-novo')
  assert.deepEqual(await second, { accepted: true, value: 'arquivo-novo' })

  firstResult.resolve('arquivo-antigo')
  assert.deepEqual(await first, { accepted: false, value: 'arquivo-antigo' })
})

test('aborta a operação anterior quando uma nova começa', async () => {
  const runner = createLatestRequestRunner()
  let firstSignal

  const first = runner.run(signal => {
    firstSignal = signal
    return new Promise(() => {})
  })
  runner.run(() => Promise.resolve('novo'))

  assert.equal(firstSignal.aborted, true)
  void first
})

test('invalidate impede uma resposta pendente de ser aceita', async () => {
  const runner = createLatestRequestRunner()
  const pendingResult = deferred()
  const pending = runner.run(() => pendingResult.promise)

  runner.invalidate()
  pendingResult.resolve('resultado-antigo')

  assert.deepEqual(await pending, { accepted: false, value: 'resultado-antigo' })
})

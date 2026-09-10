import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import test from 'node:test'

const appSource = readFileSync(new URL('../src/App.jsx', import.meta.url), 'utf8')
const searchSource = readFileSync(
  new URL('../src/features/search/index/IndexSearch.jsx', import.meta.url),
  'utf8',
)
const hashSource = readFileSync(
  new URL('../src/features/hash/HashOverflow.jsx', import.meta.url),
  'utf8',
)
const comparisonSource = readFileSync(
  new URL('../src/features/search/scan/ComparisonPanel.jsx', import.meta.url),
  'utf8',
)

function occurrences(source, fragment) {
  return source.split(fragment).length - 1
}

test('monta uma única instância de cada painel de consulta', () => {
  assert.equal(occurrences(appSource, '<IndexSearch '), 1)
  assert.equal(occurrences(appSource, '<HashOverflow '), 1)
  assert.equal(occurrences(appSource, '<ComparisonPanel'), 1)
  assert.equal(occurrences(searchSource, '>Busca por índice</h3>'), 1)
  assert.equal(occurrences(hashSource, '>Hash, colisão e overflow</h3>'), 1)
})

test('usa somente rótulos técnicos na comparação', () => {
  assert.match(comparisonSource, />Busca indexada<\/h3>/)
  assert.match(comparisonSource, />Table Scan<\/h3>/)
  assert.doesNotMatch(comparisonSource, /Busca indexada\s*\(/i)
  assert.doesNotMatch(comparisonSource, /Table Scan\s*\(/i)
})

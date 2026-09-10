import { useState } from 'react'

import FlowHeading from '../../../components/FlowHeading.jsx'
import MetricCard from '../../../components/MetricCard.jsx'
import { compareSearches, searchByScan } from './scanApi.js'

function ComparisonPanel({ dataAvailable = false, indexReady = false }) {
  const [key, setKey] = useState('')
  const [scanResult, setScanResult] = useState(null)
  const [metrics, setMetrics] = useState(null)
  const [error, setError] = useState('')
  const [loadingAction, setLoadingAction] = useState('')

  function normalizedKey() {
    const value = key.trim()
    if (!value) setError('Informe uma chave para buscar.')
    return value
  }

  async function handleScan() {
    if (!dataAvailable) {
      setError('Carregue um arquivo antes de executar o table scan.')
      return
    }
    const value = normalizedKey()
    if (!value) return

    setLoadingAction('scan')
    setError('')
    setMetrics(null)
    setScanResult(null)

    try {
      setScanResult(await searchByScan(value))
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setLoadingAction('')
    }
  }

  async function handleCompare(event) {
    event.preventDefault()
    if (!indexReady) {
      setError('Construa o índice antes de comparar os métodos de busca.')
      return
    }
    const value = normalizedKey()
    if (!value) return

    setLoadingAction('compare')
    setError('')
    setScanResult(null)
    setMetrics(null)

    try {
      setMetrics(await compareSearches(value))
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setLoadingAction('')
    }
  }

  return (
    <section className="app-panel space-y-6" aria-labelledby="comparison-heading">
      <FlowHeading
        description="Execute a varredura isoladamente ou confronte seus custos com a busca indexada."
        id="comparison-heading"
        step="4"
        title="Comparar métodos de busca"
      />

      <form className="grid gap-3 lg:grid-cols-[minmax(0,1fr)_auto_auto]" onSubmit={handleCompare}>
        <input
          aria-label="Chave para comparação"
          className="app-input min-w-0 flex-1"
          disabled={!dataAvailable || Boolean(loadingAction)}
          onChange={(event) => setKey(event.target.value)}
          placeholder="Digite uma palavra para testar nos dois métodos"
          value={key}
        />
        <button
          className="app-button-secondary w-full lg:w-auto"
          disabled={!dataAvailable || Boolean(loadingAction)}
          onClick={handleScan}
          type="button"
        >
          {loadingAction === 'scan' ? 'Executando...' : 'Executar table scan'}
        </button>
        <button
          className="app-button-primary w-full lg:w-auto"
          disabled={!indexReady || Boolean(loadingAction)}
          type="submit"
        >
          {loadingAction === 'compare' ? 'Comparando...' : 'Comparar custos'}
        </button>
      </form>

      {!dataAvailable && <p className="app-message-warning">Carregue um arquivo para habilitar o Table Scan.</p>}
      {dataAvailable && !indexReady && (
        <p className="app-message-info">O Table Scan está disponível; construa o índice para habilitar a comparação.</p>
      )}

      {error && <p className="app-message-error" role="alert">{error}</p>}

      {scanResult && (
        <div aria-live="polite" className="app-subpanel space-y-3">
          <h3 className="font-medium text-slate-800">Resultado do Table Scan</h3>
          <div className="grid gap-2 sm:grid-cols-3">
            <MetricCard label="Resultado" value={scanResult.found ? 'Encontrada' : 'Não encontrada'} />
            <MetricCard label="Página" value={scanResult.page_id ?? '-'} />
            <MetricCard label="Páginas lidas" value={scanResult.pages_read} tone="teal" />
          </div>
          <p className="text-xs text-slate-500">Tempo: {(scanResult.elapsed_time * 1000).toFixed(4)} ms</p>
          <p className="text-xs text-slate-500">{scanResult.trace}</p>
        </div>
      )}

      {metrics && (
        <div className="space-y-6" aria-live="polite">
          <div className="grid gap-6 md:grid-cols-2">
            <article className="app-subpanel space-y-4">
              <h3 className="font-semibold text-indigo-800">Busca indexada</h3>
              <div className="grid gap-2 sm:grid-cols-2">
                <MetricCard label="Resultado" value={metrics.index_search.found ? 'Encontrada' : 'Não encontrada'} />
                <MetricCard label="Página acessada" value={metrics.index_search.page_id ?? '-'} />
                <MetricCard label="Páginas lidas" value={metrics.index_search.pages_read} tone="indigo" />
              </div>
              <p className="text-xs text-slate-500">
                Tempo: {(metrics.index_search.elapsed_time * 1000).toFixed(4)} ms
              </p>
            </article>

            <article className="app-subpanel space-y-4">
              <h3 className="font-semibold text-teal-800">Table Scan</h3>
              <div className="grid gap-2 sm:grid-cols-2">
                <MetricCard label="Resultado" value={metrics.table_scan.found ? 'Encontrada' : 'Não encontrada'} />
                <MetricCard label="Página encontrada" value={metrics.table_scan.page_id ?? '-'} />
                <MetricCard label="Páginas lidas" value={metrics.table_scan.pages_read} tone="teal" />
              </div>
              <p className="text-xs text-slate-500">
                Tempo: {(metrics.table_scan.elapsed_time * 1000).toFixed(4)} ms
              </p>
            </article>
          </div>

          <div className="rounded-xl border border-emerald-200 bg-emerald-50/70 p-5">
            <h3 className="mb-4 text-lg font-semibold text-emerald-900">Diferença de custos</h3>
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              <div>
                <p className="text-xs font-medium uppercase tracking-wide text-emerald-700">Páginas economizadas</p>
                <p className="mt-1 text-xl font-semibold text-emerald-900">{metrics.pages_saved} ({metrics.page_savings_percentage.toFixed(2)}%)</p>
              </div>
              <div>
                <p className="text-xs font-medium uppercase tracking-wide text-emerald-700">Diferença de tempo</p>
                <p className="mt-1 text-xl font-semibold text-emerald-900">{(metrics.time_difference_seconds * 1000).toFixed(2)} ms</p>
              </div>
              <div>
                <p className="text-xs font-medium uppercase tracking-wide text-emerald-700">Diferença percentual</p>
                <p className="mt-1 text-xl font-semibold text-emerald-900">{metrics.time_savings_percentage.toFixed(2)}%</p>
              </div>
              <div>
                <p className="text-xs font-medium uppercase tracking-wide text-emerald-700">Fator de aceleração</p>
                <p className="mt-1 text-xl font-semibold text-emerald-900">{metrics.speedup_factor}x</p>
              </div>
            </div>
          </div>

          {!metrics.results_agree && (
            <p className="app-message-error" role="alert">As estratégias produziram resultados diferentes. Reconstrua o índice antes de comparar.</p>
          )}

          <p className="text-xs text-slate-500">Caminho do Table Scan: {metrics.table_scan.trace}</p>
        </div>
      )}
    </section>
  )
}

export default ComparisonPanel

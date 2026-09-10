import { useState } from 'react'

import MetricCard from '../../../components/MetricCard.jsx'
import { searchByIndex } from './searchApi.js'

function IndexSearch({ disabled = false, search = searchByIndex }) {
  const [key, setKey] = useState('')
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()

    if (disabled) {
      setError('Construa o índice antes de realizar uma busca indexada.')
      return
    }

    if (!key.trim()) {
      setError('Informe uma chave de busca.')
      return
    }

    setLoading(true)
    setError('')

    try {
      setResult(await search(key.trim()))
    } catch (requestError) {
      setResult(null)
      setError(requestError.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <article className="app-panel space-y-5" aria-labelledby="index-search-heading">
      <div>
        <h3 className="text-lg font-semibold text-slate-900" id="index-search-heading">Busca por índice</h3>
        <p className="mt-1 text-sm leading-6 text-slate-600">
          Localize uma chave e veja o custo do acesso direto.
        </p>
      </div>

      <form className="flex flex-col gap-3 md:flex-row" onSubmit={handleSubmit}>
        <input
          aria-label="Chave para busca indexada"
          className="app-input min-w-0 flex-1"
          disabled={disabled || loading}
          onChange={(event) => setKey(event.target.value)}
          placeholder="Digite uma palavra"
          value={key}
        />
        <button
          className="app-button-primary w-full md:w-auto"
          disabled={disabled || loading}
          type="submit"
        >
          {loading ? 'Buscando...' : 'Buscar'}
        </button>
      </form>

      {disabled && <p className="app-message-warning">Busca bloqueada até a construção do índice.</p>}

      {error && (
        <p aria-live="polite" className="app-message-error" role="alert">
          {error}
        </p>
      )}

      {result && (
        <div aria-live="polite" className="space-y-4">
          <p className={result.found ? 'font-medium text-emerald-700' : 'font-medium text-amber-700'}>
            {result.found ? 'Chave encontrada' : 'Chave não encontrada'}
          </p>

          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-2 2xl:grid-cols-3">
            <MetricCard label="Bucket" value={result.bucket_id} tone="indigo" />
            <MetricCard label="Página" value={result.page_id ?? '-'} tone="indigo" />
            <MetricCard label="Páginas lidas" value={result.pages_read} />
          </div>

          <p className="text-sm text-slate-500">
            Tempo: {(result.elapsed_time * 1000).toFixed(4)} ms
          </p>

          <div className="space-y-2">
            <h4 className="text-sm font-medium text-slate-700">Caminho da busca</h4>
            <ol className="flex flex-wrap items-center gap-2 text-sm">
              {result.trace.map((step, index) => (
                <li className="flex items-center gap-2" key={`${index}-${step}`}>
                  {index > 0 && <span className="text-indigo-400">→</span>}
                  <span className="rounded-full bg-slate-100 px-3 py-1 text-slate-700">{step}</span>
                </li>
              ))}
            </ol>
          </div>
        </div>
      )}
    </article>
  )
}

export default IndexSearch

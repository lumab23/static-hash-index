import { useState } from 'react'

import MetricCard from '../../components/MetricCard.jsx'
import { getHashOverflow } from './hashApi.js'

function HashOverflow({ disabled = false }) {
  const [key, setKey] = useState('')
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(event) {
    event.preventDefault()
    setData(null)
    setError('')
    if (disabled) {
      setError('Construa o índice antes de consultar hash e overflow.')
      return
    }
    if (!key.trim()) {
      setError('Informe uma chave.')
      return
    }
    setLoading(true)
    try {
      setData(await getHashOverflow(key))
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <article className="app-panel space-y-5" aria-labelledby="hash-heading">
      <div>
        <h3 id="hash-heading" className="text-lg font-semibold text-slate-900">Hash, colisão e overflow</h3>
        <p className="mt-1 text-sm leading-6 text-slate-600">Veja a distribuição de uma chave sem executar uma busca nos registros.</p>
      </div>
      <form onSubmit={handleSubmit} className="flex flex-col gap-3 md:flex-row md:items-end">
        <div className="flex-1 space-y-2">
          <label htmlFor="hash-key" className="block text-sm font-medium text-slate-700">Chave</label>
          <input id="hash-key" value={key} required disabled={disabled || loading}
            onChange={event => { setKey(event.target.value); setData(null); setError('') }}
            className="app-input" />
        </div>
        <button type="submit" disabled={disabled || loading}
          className="app-button-primary w-full md:w-auto">
          {loading ? 'Consultando...' : 'Consultar hash'}
        </button>
      </form>
      {disabled && <p className="app-message-warning">Consulta bloqueada até a construção do índice.</p>}
      {loading && <p role="status" className="app-message-info">Consultando hash...</p>}
      {error && <p role="alert" className="app-message-error">{error}</p>}
      {data && (
        <div className="space-y-5" aria-live="polite">
          <p className="break-all text-sm text-slate-600">Chave consultada: <strong className="text-slate-900">{data.key}</strong></p>
          <div className="grid gap-3 sm:grid-cols-2">
            <MetricCard label="Bucket calculado" value={data.bucket_id} tone="indigo" />
            <MetricCard label="Ocupação principal" value={`${data.bucket_occupancy} / ${data.bucket_capacity}`} />
            <MetricCard label="Total de colisões" value={data.collision_count} />
            <MetricCard label="Taxa de colisão" value={`${data.collision_rate.toFixed(2)}%`} />
            <MetricCard label="Buckets com overflow" value={data.overflow_bucket_count} tone="teal" />
            <MetricCard label="Taxa de overflow" value={`${data.overflow_rate.toFixed(2)}%`} tone="teal" />
          </div>
          {data.bucket_occupancy === data.bucket_capacity && <p className="app-message-warning">O bucket primário está cheio.</p>}
          <div className="app-subpanel space-y-2">
            <h4 className="font-medium text-slate-800">Entradas adicionais do bucket {data.bucket_id}</h4>
            {data.overflow_entries.length ? (
              <ul className="max-h-52 list-inside list-disc overflow-auto break-all text-sm text-slate-700">
                {data.overflow_entries.map((entry, position) => <li key={position}>{entry}</li>)}
              </ul>
            ) : <p className="text-sm text-slate-500">Este bucket não possui entradas adicionais.</p>}
          </div>
        </div>
      )}
    </article>
  )
}

export default HashOverflow

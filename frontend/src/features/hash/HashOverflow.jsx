import { useState } from 'react'

import { getHashOverflow } from './hashApi.js'

function HashOverflow() {
  const [key, setKey] = useState('')
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(event) {
    event.preventDefault()
    setData(null)
    setError('')
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
    <section className="space-y-5 rounded-2xl bg-slate-900 p-6" aria-labelledby="hash-heading">
      <h2 id="hash-heading" className="text-xl font-semibold">Hash, Colisão e Overflow</h2>
      <p className="text-sm text-slate-400">Consulte o bucket de uma chave no índice construído. A consulta não insere registros nem confirma a presença da chave.</p>
      <form onSubmit={handleSubmit} className="flex flex-col gap-3 sm:flex-row sm:items-end">
        <div className="flex-1 space-y-2">
          <label htmlFor="hash-key" className="block text-sm">Chave</label>
          <input id="hash-key" value={key} required disabled={loading}
            onChange={event => { setKey(event.target.value); setData(null); setError('') }}
            className="w-full rounded-lg border border-slate-700 bg-slate-950 px-4 py-2 focus-visible:outline-2 focus-visible:outline-cyan-400" />
        </div>
        <button type="submit" disabled={loading}
          className="rounded-lg bg-cyan-400 px-4 py-2 font-medium text-slate-950 focus-visible:outline-2 focus-visible:outline-cyan-300 disabled:opacity-50">
          Consultar hash
        </button>
      </form>
      {loading && <p role="status">Consultando hash...</p>}
      {error && <p role="alert" className="text-red-300">{error}</p>}
      {data && (
        <div className="space-y-5" aria-live="polite">
          <div>
            <h3 className="font-semibold">Cálculo do Hash</h3>
            <p className="break-all">Chave: <strong>{data.key}</strong></p>
            <p>hash(chave) = <strong>{data.bucket_id}</strong></p>
            <p>Bucket escolhido: <strong>{data.bucket_id}</strong></p>
          </div>
          <div>
            <h3 className="font-semibold">Ocupação do Bucket</h3>
            <p>{data.bucket_occupancy} / {data.bucket_capacity}</p>
            {data.bucket_occupancy === data.bucket_capacity && <p className="text-amber-300">Bucket primário cheio</p>}
          </div>
          <div>
            <h3 className="font-semibold">Colisões no índice</h3>
            <p>Inserções que encontraram o bucket primário cheio: {data.collision_count}</p>
            <p>Taxa sobre o total de entradas: {data.collision_rate.toFixed(2)}%</p>
          </div>
          <div>
            <h3 className="font-semibold">Overflow no índice</h3>
            <p>Buckets com overflow: {data.overflow_bucket_count}</p>
            <p>Taxa sobre o total de buckets: {data.overflow_rate.toFixed(2)}%</p>
            <h4 className="mt-3 font-medium">Entradas de overflow do bucket {data.bucket_id}</h4>
            {data.overflow_entries.length ? (
              <ul className="list-inside list-disc break-all">
                {data.overflow_entries.map((entry, position) => <li key={position}>{entry}</li>)}
              </ul>
            ) : <p>Este bucket não possui entradas em overflow.</p>}
          </div>
        </div>
      )}
    </section>
  )
}

export default HashOverflow

import { useState } from 'react'

import { getIndexBucket } from './indexApi.js'

export default function BucketExplorer({ nb, onIndexMissing }) {
  const [id, setId] = useState('0')
  const [bucket, setBucket] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(event) {
    event.preventDefault()
    const bucketId = Number(id)
    if (!id.trim() || !Number.isSafeInteger(bucketId) || bucketId < 0 || bucketId >= nb) {
      setError(`Informe um ID inteiro entre 0 e ${nb - 1}.`)
      return
    }
    setLoading(true)
    setError('')
    setBucket(null)
    try {
      setBucket(await getIndexBucket(bucketId))
    } catch (requestError) {
      if (requestError.status === 409) onIndexMissing()
      else setError(requestError.status === 404 ? 'Bucket não encontrado. Atualize o resumo do índice.' : requestError.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <section aria-labelledby="bucket-heading" className="app-panel space-y-5">
      <div>
        <h2 id="bucket-heading" className="text-lg font-semibold text-slate-900">Detalhes de um bucket</h2>
        <p className="mt-1 text-sm text-slate-600">Consulte somente o bucket necessário e veja suas entradas primárias e blocos adicionais.</p>
      </div>
      <form className="flex flex-col gap-3 md:flex-row md:items-end" onSubmit={handleSubmit}>
        <div className="flex-1 space-y-2">
          <label className="block text-sm font-medium text-slate-700" htmlFor="bucket-id">ID do bucket</label>
          <input id="bucket-id" type="number" min="0" max={nb - 1} step="1" required
            aria-describedby="bucket-range" value={id} onChange={event => setId(event.target.value)}
            disabled={loading}
            className="app-input" />
          <p id="bucket-range" className="text-sm text-slate-500">IDs disponíveis: 0 até {nb - 1}. Apenas o bucket escolhido será consultado.</p>
        </div>
        <button type="submit" disabled={loading}
          className="app-button-secondary w-full md:w-auto">
          {loading ? 'Consultando...' : 'Consultar bucket'}
        </button>
      </form>
      {loading && <p role="status" className="app-message-info">Consultando bucket...</p>}
      {error && <p role="alert" className="app-message-error">{error}</p>}
      {bucket && (
        <div className="space-y-5" aria-live="polite">
          <h3 className="text-lg font-medium">Bucket {bucket.id}</h3>
          <p className="text-sm text-slate-600">Capacidade: {bucket.capacity} · Ocupação principal: {bucket.primary_count}/{bucket.capacity} · Total de entradas: {bucket.total_entries}</p>
          {bucket.total_entries === 0 && <p className="text-slate-500">Este bucket está vazio.</p>}
          <EntryTable title="Área principal" entries={bucket.primary_entries} />
          <h3 className="text-lg font-medium">Overflow</h3>
          {!bucket.has_overflow && <p className="text-slate-500">Este bucket não possui overflow.</p>}
          {bucket.overflow_blocks.map(block => (
            <div className="rounded-lg border border-amber-200 bg-amber-50/60 p-4" key={block.block}>
              <EntryTable title={`Bloco ${block.block} de overflow · ${block.count} entrada(s)`} entries={block.entries} />
            </div>
          ))}
        </div>
      )}
    </section>
  )
}

function EntryTable({ title, entries }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full table-fixed text-left text-sm">
        <caption className="pb-3 text-left font-medium text-slate-700">{title}</caption>
        <thead className="border-b border-slate-200 text-slate-500">
          <tr><th scope="col" className="w-2/3 p-2">Chave</th><th scope="col" className="p-2">Página (page_id)</th></tr>
        </thead>
        <tbody>
          {entries.map((entry, position) => (
            <tr className="border-b border-slate-100" key={position}>
              <td className="whitespace-pre-wrap break-all p-2 font-mono">{entry.key}</td>
              <td className="p-2">{entry.page_id}</td>
            </tr>
          ))}
          {entries.length === 0 && <tr><td colSpan="2" className="p-2 text-slate-500">Nenhuma entrada nesta área.</td></tr>}
        </tbody>
      </table>
    </div>
  )
}

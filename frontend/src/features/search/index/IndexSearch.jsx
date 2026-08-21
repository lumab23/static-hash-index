import { useState } from 'react'

import { searchByIndex } from './searchApi.js'

function IndexSearch({ search = searchByIndex }) {
  const [key, setKey] = useState('')
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()

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
    <section className="space-y-6 rounded-2xl bg-slate-900 p-6 text-slate-100">
      <div>
        <h2 className="text-xl font-semibold">Busca por índice</h2>
        <p className="text-sm text-slate-400">
          Informe uma chave para visualizar o caminho até a página de dados.
        </p>
      </div>

      <form className="flex gap-3" onSubmit={handleSubmit}>
        <input
          className="min-w-0 flex-1 rounded-lg border border-slate-700 bg-slate-950 px-4 py-2 outline-none focus:border-cyan-400"
          onChange={(event) => setKey(event.target.value)}
          placeholder="Digite uma palavra"
          value={key}
        />
        <button
          className="rounded-lg bg-cyan-400 px-4 py-2 font-medium text-slate-950 disabled:opacity-50"
          disabled={loading}
          type="submit"
        >
          {loading ? 'Buscando...' : 'Buscar'}
        </button>
      </form>

      {error && <p className="text-sm text-red-400">{error}</p>}

      {result && (
        <div className="space-y-4">
          <p className={result.found ? 'text-emerald-400' : 'text-amber-400'}>
            {result.found ? 'Chave encontrada' : 'Chave não encontrada'}
          </p>

          <div className="grid gap-3 sm:grid-cols-3">
            <ResultCard label="Bucket" value={result.bucket_id} highlight />
            <ResultCard label="Página" value={result.page_id ?? '-'} highlight />
            <ResultCard label="Páginas lidas" value={result.pages_read} />
          </div>

          <p className="text-sm text-slate-400">
            Tempo: {(result.elapsed_time * 1000).toFixed(4)} ms
          </p>

          <ol className="flex flex-wrap items-center gap-2 text-sm">
            {result.trace.map((step) => (
              <li className="rounded-full bg-slate-800 px-3 py-1" key={step}>
                {step}
              </li>
            ))}
          </ol>
        </div>
      )}
    </section>
  )
}

function ResultCard({ label, value, highlight = false }) {
  const color = highlight ? 'border-cyan-400 bg-cyan-400/10' : 'border-slate-700 bg-slate-950'

  return (
    <div className={`rounded-lg border p-3 ${color}`}>
      <p className="text-xs uppercase text-slate-400">{label}</p>
      <p className="mt-1 text-lg font-semibold">{value}</p>
    </div>
  )
}

export default IndexSearch

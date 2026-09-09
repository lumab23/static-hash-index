import { useEffect, useState } from 'react'

import BucketExplorer from './BucketExplorer.jsx'
import IndexSummary from './IndexSummary.jsx'
import { buildIndex, getIndexSummary } from './indexApi.js'

export default function IndexPanel({ onIndexChanged }) {
  const [fr, setFr] = useState('50')
  const [summary, setSummary] = useState(null)
  const [loadingSummary, setLoadingSummary] = useState(true)
  const [building, setBuilding] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [revision, setRevision] = useState(0)

  useEffect(() => {
    let active = true
    getIndexSummary().then(result => {
      if (active) setSummary(result)
    }).catch(requestError => {
      if (active && requestError.status !== 409) setError(requestError.message)
    }).finally(() => {
      if (active) setLoadingSummary(false)
    })
    return () => { active = false }
  }, [])

  function clearIndex() {
    setSummary(null)
    setSuccess('')
    setError('O índice não está disponível. Carregue os dados e construa o índice novamente.')
    onIndexChanged()
  }

  async function refreshSummary() {
    setLoadingSummary(true)
    setError('')
    setSuccess('')
    setRevision(value => value + 1)
    try {
      setSummary(await getIndexSummary())
      onIndexChanged()
    } catch (requestError) {
      if (requestError.status === 409) {
        setSummary(null)
        onIndexChanged()
      } else setError(requestError.message)
    } finally {
      setLoadingSummary(false)
    }
  }

  async function handleBuild(event) {
    event.preventDefault()
    const capacity = Number(fr)
    if (!fr.trim() || !Number.isSafeInteger(capacity) || capacity <= 0) {
      setError('Informe FR como um número inteiro maior que zero.')
      return
    }
    setBuilding(true)
    setError('')
    setSuccess('')
    setRevision(value => value + 1)
    try {
      const result = await buildIndex(capacity)
      setSummary(result)
      setSuccess('Índice construído com sucesso.')
      onIndexChanged()
    } catch (requestError) {
      if (requestError.status === 409) {
        setSummary(null)
        onIndexChanged()
        setError('Carregue primeiro um arquivo TXT pela API de dados. Depois, tente construir o índice novamente.')
      } else setError(requestError.message)
    } finally {
      setBuilding(false)
    }
  }

  return (
    <div className="space-y-8">
      <section aria-labelledby="build-heading" className="space-y-5 rounded-2xl bg-slate-900 p-6">
        <h2 id="build-heading" className="text-xl font-semibold">Construir índice</h2>
        <p className="text-sm text-slate-400">Use as páginas do TXT já carregado. FR limita as entradas de cada bucket primário; NB será calculado automaticamente.</p>
        <form className="flex flex-col gap-3 sm:flex-row sm:items-end" onSubmit={handleBuild}>
          <div className="flex-1 space-y-2">
            <label htmlFor="index-fr" className="block text-sm">Capacidade do bucket (FR)</label>
            <input id="index-fr" type="number" min="1" step="1" required value={fr}
              onChange={event => setFr(event.target.value)} disabled={building || loadingSummary}
              className="w-full rounded-lg border border-slate-700 bg-slate-950 px-4 py-2 focus-visible:outline-2 focus-visible:outline-cyan-400" />
          </div>
          <button type="submit" disabled={building || loadingSummary}
            className="rounded-lg bg-cyan-400 px-4 py-2 font-medium text-slate-950 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cyan-300 disabled:opacity-50">
            {building ? 'Construindo...' : 'Construir índice'}
          </button>
        </form>
        {building && <p role="status">Construindo o índice. Aguarde...</p>}
        {error && <p role="alert" className="text-red-300">{error}</p>}
        {success && <p role="status" className="text-emerald-300">{success}</p>}
        <div className="flex flex-wrap items-center justify-between gap-3">
          <h3 className="font-medium">Resumo atual</h3>
          <button type="button" onClick={refreshSummary} disabled={building || loadingSummary}
            className="rounded px-2 py-1 text-sm text-cyan-300 underline underline-offset-4 focus-visible:outline-2 focus-visible:outline-cyan-400 disabled:opacity-50">
            Atualizar resumo
          </button>
        </div>
        {loadingSummary ? <p role="status">Consultando resumo...</p>
          : summary ? <IndexSummary summary={summary} />
            : <p className="text-slate-400">Índice ainda não construído.</p>}
      </section>
      {summary && !building && !loadingSummary && (
        <BucketExplorer key={revision} nb={summary.nb} onIndexMissing={clearIndex} />
      )}
    </div>
  )
}

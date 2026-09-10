import { useEffect, useState } from 'react'

import FlowHeading from '../../components/FlowHeading.jsx'
import BucketExplorer from './BucketExplorer.jsx'
import IndexSummary from './IndexSummary.jsx'
import { buildIndex, getIndexSummary } from './indexApi.js'

export default function IndexPanel({ dataAvailable, disabled, onIndexBuilt, onIndexStateChange }) {
  const [fr, setFr] = useState('50')
  const [summary, setSummary] = useState(null)
  const [loadingSummary, setLoadingSummary] = useState(true)
  const [building, setBuilding] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [revision, setRevision] = useState(0)

  useEffect(() => {
    if (!dataAvailable) {
      setSummary(null)
      setLoadingSummary(false)
      onIndexStateChange('unavailable')
      return undefined
    }

    let active = true
    setLoadingSummary(true)
    onIndexStateChange('checking')
    getIndexSummary().then(result => {
      if (active) {
        setSummary(result)
        onIndexStateChange('ready')
      }
    }).catch(requestError => {
      if (!active) return
      if (requestError.status === 409) {
        setSummary(null)
        onIndexStateChange('unavailable')
      } else {
        setError(requestError.message)
        onIndexStateChange('error')
      }
    }).finally(() => {
      if (active) setLoadingSummary(false)
    })
    return () => { active = false }
  }, [dataAvailable, onIndexStateChange])

  function clearIndex() {
    setSummary(null)
    setSuccess('')
    setError('O índice não está disponível. Carregue os dados e construa o índice novamente.')
    onIndexStateChange('unavailable')
  }

  async function refreshSummary() {
    setLoadingSummary(true)
    setError('')
    setSuccess('')
    setRevision(value => value + 1)
    try {
      setSummary(await getIndexSummary())
      onIndexStateChange('ready')
    } catch (requestError) {
      if (requestError.status === 409) {
        setSummary(null)
        onIndexStateChange('unavailable')
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
    onIndexStateChange('building')
    try {
      const result = await buildIndex(capacity)
      setSummary(result)
      setSuccess('Índice construído com sucesso.')
      onIndexBuilt()
    } catch (requestError) {
      if (requestError.status === 409) {
        setSummary(null)
        onIndexStateChange('unavailable')
        setError('Carregue primeiro um arquivo TXT pela API de dados. Depois, tente construir o índice novamente.')
      } else {
        setError(requestError.message)
        onIndexStateChange('error')
      }
    } finally {
      setBuilding(false)
    }
  }

  return (
    <div className="space-y-8">
      <section aria-labelledby="build-heading" className="app-panel space-y-5">
        <FlowHeading
          description="Defina a capacidade dos buckets primários. A quantidade de buckets é calculada automaticamente."
          id="build-heading"
          step="2"
          title="Construir e explorar o índice"
        />
        <form className="flex flex-col gap-3 md:flex-row md:items-end" onSubmit={handleBuild}>
          <div className="flex-1 space-y-2">
            <label htmlFor="index-fr" className="block text-sm font-medium text-slate-700">Capacidade do bucket (FR)</label>
            <input id="index-fr" type="number" min="1" step="1" required value={fr}
              onChange={event => setFr(event.target.value)} disabled={disabled || !dataAvailable || building || loadingSummary}
              className="app-input" />
          </div>
          <button type="submit" disabled={disabled || !dataAvailable || building || loadingSummary}
            className="app-button-primary w-full md:w-auto">
            {building ? 'Construindo...' : 'Construir índice'}
          </button>
        </form>
        {!dataAvailable && <p className="app-message-info">Carregue um arquivo TXT antes de construir o índice.</p>}
        {disabled && <p role="status" className="app-message-warning">Aguarde o carregamento do novo arquivo.</p>}
        {building && <p role="status" className="app-message-info">Construindo o índice. Aguarde...</p>}
        {error && <p role="alert" className="app-message-error">{error}</p>}
        {success && <p role="status" className="app-message-success">{success}</p>}
        <div className="flex flex-wrap items-center justify-between gap-3">
          <h3 className="font-medium text-slate-800">Resumo do índice</h3>
          <button type="button" onClick={refreshSummary} disabled={disabled || !dataAvailable || building || loadingSummary}
            className="rounded px-2 py-1 text-sm font-medium text-indigo-700 underline decoration-indigo-200 underline-offset-4 focus-visible:outline-2 focus-visible:outline-indigo-500 disabled:text-slate-400">
            Atualizar resumo
          </button>
        </div>
        {loadingSummary ? <p className="text-sm text-slate-600" role="status">Consultando resumo...</p>
          : summary ? <IndexSummary summary={summary} />
            : <p className="text-sm text-slate-500">Índice ainda não construído.</p>}
      </section>
      {summary && !building && !loadingSummary && (
        <BucketExplorer key={revision} nb={summary.nb} onIndexMissing={clearIndex} />
      )}
    </div>
  )
}

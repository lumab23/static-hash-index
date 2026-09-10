import { useEffect, useRef, useState } from 'react'

import FlowHeading from '../../components/FlowHeading.jsx'
import { getPageRecords, getPagesSummary, loadData } from './dataApi.js'
import { createLatestRequestRunner } from './latestRequest.js'

const PAGE_RECORD_LIMIT = 100

function DataPanel({ onStateChange }) {
  const [file, setFile] = useState(null)
  const [pageSize, setPageSize] = useState('100')
  const [summary, setSummary] = useState(null)
  const [pageId, setPageId] = useState('0')
  const [pageResult, setPageResult] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [pageLoading, setPageLoading] = useState(false)
  const [error, setError] = useState('')
  const [pageError, setPageError] = useState('')
  const [success, setSuccess] = useState('')
  const fileInputRef = useRef(null)
  const dataRequests = useRef(createLatestRequestRunner())
  const pageRequests = useRef(createLatestRequestRunner())

  useEffect(() => {
    let mounted = true
    dataRequests.current.run(signal => getPagesSummary(signal)).then(outcome => {
      if (!mounted || !outcome.accepted) return
      setSummary(outcome.value)
      onStateChange({ status: 'loaded', hasData: true, newDataset: false })
    }).catch(requestError => {
      if (!mounted) return
      if (requestError.status === 409) {
        onStateChange({ status: 'empty', hasData: false, newDataset: false })
      } else {
        setError(requestError.message)
        onStateChange({ status: 'error', hasData: false, newDataset: false })
      }
    })

    return () => {
      mounted = false
      dataRequests.current.invalidate()
      pageRequests.current.invalidate()
    }
  }, [onStateChange])

  function validateUpload() {
    if (!file) return 'Selecione um arquivo TXT.'
    if (!file.name.toLowerCase().endsWith('.txt')) return 'O arquivo deve possuir extensão .txt.'
    const parsedPageSize = Number(pageSize)
    if (!pageSize.trim() || !Number.isSafeInteger(parsedPageSize) || parsedPageSize <= 0) {
      return 'Informe o tamanho da página como um inteiro maior que zero.'
    }
    return ''
  }

  async function handleUpload(event) {
    event.preventDefault()
    if (uploading) return

    const validationError = validateUpload()
    if (validationError) {
      setError(validationError)
      return
    }

    setUploading(true)
    setError('')
    setSuccess('')
    setPageError('')
    onStateChange({ status: 'uploading', hasData: Boolean(summary), newDataset: false })

    try {
      const outcome = await dataRequests.current.run(signal => (
        loadData(file, Number(pageSize), signal)
      ))
      if (!outcome.accepted) return

      pageRequests.current.invalidate()
      setSummary(outcome.value)
      setPageId('0')
      setPageResult(null)
      setPageLoading(false)
      setFile(null)
      if (fileInputRef.current) fileInputRef.current.value = ''
      setSuccess('Arquivo carregado. Construa um novo índice para habilitar a busca indexada.')
      onStateChange({ status: 'loaded', hasData: true, newDataset: true })
      setUploading(false)
    } catch (requestError) {
      setError(requestError.message)
      onStateChange({ status: 'error', hasData: Boolean(summary), newDataset: false })
      setUploading(false)
    }
  }

  async function loadPage(offset = 0) {
    const parsedPageId = Number(pageId)
    if (!Number.isSafeInteger(parsedPageId) || parsedPageId < 0) {
      setPageError('Informe um ID de página inteiro maior ou igual a zero.')
      return
    }
    if (summary && parsedPageId >= summary.total_pages) {
      setPageError(`A página deve estar entre 0 e ${summary.total_pages - 1}.`)
      return
    }

    setPageLoading(true)
    setPageError('')
    try {
      const outcome = await pageRequests.current.run(signal => (
        getPageRecords(parsedPageId, offset, PAGE_RECORD_LIMIT, signal)
      ))
      if (!outcome.accepted) return
      setPageResult(outcome.value)
      setPageLoading(false)
    } catch (requestError) {
      setPageResult(null)
      setPageError(requestError.message)
      setPageLoading(false)
    }
  }

  function handlePageSubmit(event) {
    event.preventDefault()
    if (!pageLoading) loadPage(0)
  }

  return (
    <section className="app-panel space-y-6" aria-labelledby="data-heading">
      <FlowHeading
        description="Envie um TXT com uma palavra por linha e defina quantos registros cada página terá."
        id="data-heading"
        step="1"
        title="Carregar dados e consultar páginas"
      />

      <form className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_12rem_auto] lg:items-end" onSubmit={handleUpload}>
        <div className="min-w-0 space-y-2">
          <label className="block text-sm font-medium text-slate-700" htmlFor="data-file">Arquivo TXT</label>
          <input
            accept=".txt,text/plain"
            className="app-input block min-w-0 overflow-hidden text-sm file:mr-3 file:rounded-md file:border-0 file:bg-indigo-50 file:px-3 file:py-1.5 file:font-medium file:text-indigo-700"
            disabled={uploading}
            id="data-file"
            onChange={event => {
              setFile(event.target.files?.[0] ?? null)
              setError('')
              setSuccess('')
            }}
            ref={fileInputRef}
            type="file"
          />
        </div>
        <div className="space-y-2">
          <label className="block text-sm font-medium text-slate-700" htmlFor="page-size">Tamanho da página</label>
          <input
            className="app-input"
            disabled={uploading}
            id="page-size"
            min="1"
            onChange={event => {
              setPageSize(event.target.value)
              setError('')
            }}
            required
            step="1"
            type="number"
            value={pageSize}
          />
        </div>
        <button
          className="app-button-primary w-full lg:w-auto"
          disabled={uploading}
          type="submit"
        >
          {uploading ? 'Carregando...' : 'Carregar arquivo'}
        </button>
      </form>

      {uploading && <p role="status" className="app-message-info">Processando o arquivo e criando as páginas...</p>}
      {error && <p role="alert" className="app-message-error">{error}</p>}
      {success && <p role="status" className="app-message-success">{success}</p>}

      {summary && (
        <div className="space-y-6" aria-live="polite">
          <dl className="grid gap-3 sm:grid-cols-3">
            <SummaryCard label="Total de registros" value={summary.total_records} />
            <SummaryCard label="Total de páginas" value={summary.total_pages} />
            <SummaryCard label="Registros por página" value={summary.page_size} />
          </dl>

          <div className="grid gap-4 lg:grid-cols-2">
            <PagePreview label="Primeira página" page={summary.first_page} />
            <PagePreview label="Última página" page={summary.last_page} />
          </div>

          <div className="app-subpanel space-y-4">
            <div>
              <h3 className="font-semibold">Consultar página por ID</h3>
              <p className="text-sm text-slate-600">IDs começam em 0. Exibimos no máximo {PAGE_RECORD_LIMIT} registros por consulta.</p>
            </div>
            <form className="flex flex-col gap-3 md:flex-row" onSubmit={handlePageSubmit}>
              <input
                aria-label="ID da página"
                className="app-input min-w-0 flex-1"
                disabled={pageLoading}
                max={summary.total_pages - 1}
                min="0"
                onChange={event => {
                  setPageId(event.target.value)
                  setPageResult(null)
                  setPageError('')
                  pageRequests.current.invalidate()
                }}
                required
                step="1"
                type="number"
                value={pageId}
              />
              <button
                className="app-button-secondary w-full md:w-auto"
                disabled={pageLoading}
                type="submit"
              >
                {pageLoading ? 'Consultando...' : 'Consultar página'}
              </button>
            </form>
            {pageError && <p className="app-message-error" role="alert">{pageError}</p>}
            {pageResult && (
              <div className="space-y-3">
                <p className="text-sm text-slate-600">
                  Página {pageResult.id}: registros {pageResult.offset + 1}–{Math.min(
                    pageResult.offset + pageResult.records.length,
                    pageResult.total_records,
                  )} de {pageResult.total_records}
                </p>
                <RecordList records={pageResult.records} />
                <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 sm:justify-start">
                  <button
                    className="app-button-secondary min-h-9 w-full px-3 py-1.5 text-sm"
                    disabled={pageLoading || !pageResult.has_previous}
                    onClick={() => loadPage(Math.max(0, pageResult.offset - PAGE_RECORD_LIMIT))}
                    type="button"
                  >
                    Anteriores
                  </button>
                  <button
                    className="app-button-secondary min-h-9 w-full px-3 py-1.5 text-sm"
                    disabled={pageLoading || !pageResult.has_next}
                    onClick={() => loadPage(pageResult.offset + PAGE_RECORD_LIMIT)}
                    type="button"
                  >
                    Próximos
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </section>
  )
}

function SummaryCard({ label, value }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
      <dt className="text-sm text-slate-500">{label}</dt>
      <dd className="mt-2 text-xl font-semibold text-indigo-700">{value.toLocaleString('pt-BR')}</dd>
    </div>
  )
}

function PagePreview({ label, page }) {
  return (
    <article className="app-subpanel space-y-3">
      <div className="flex items-center justify-between gap-3">
        <h3 className="font-semibold">{label}</h3>
        <span className="rounded-full bg-indigo-100 px-3 py-1 text-sm font-medium text-indigo-700">ID {page.id}</span>
      </div>
      <RecordList records={page.records} />
      <p className="text-xs text-slate-500">Prévia limitada aos primeiros cinco registros da página.</p>
    </article>
  )
}

function RecordList({ records }) {
  if (!records.length) return <p className="text-sm text-slate-500">Nenhum registro neste intervalo.</p>
  return (
    <ol className="max-h-64 space-y-1 overflow-auto rounded-lg border border-slate-200 bg-white p-3 text-sm text-slate-700">
      {records.map((record, index) => (
        <li className="break-all border-b border-slate-100 py-1.5 last:border-0" key={`${index}-${record}`}>
          {record}
        </li>
      ))}
    </ol>
  )
}

export default DataPanel

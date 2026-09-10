import { useCallback, useState } from 'react'

import FlowHeading from './components/FlowHeading.jsx'
import DataPanel from './features/data/DataPanel.jsx'
import IndexPanel from './features/index/IndexPanel.jsx'
import HashOverflow from './features/hash/HashOverflow.jsx'
import IndexSearch from './features/search/index/IndexSearch.jsx'
import ComparisonPanel from './features/search/scan/ComparisonPanel.jsx'

function App() {
  const [dataStatus, setDataStatus] = useState('checking')
  const [hasData, setHasData] = useState(false)
  const [datasetRevision, setDatasetRevision] = useState(0)
  const [indexStatus, setIndexStatus] = useState('unavailable')
  const [indexRevision, setIndexRevision] = useState(0)

  const handleDataStateChange = useCallback(({ status, hasData: available, newDataset }) => {
    setDataStatus(status)
    setHasData(available)
    if (newDataset) {
      setDatasetRevision(value => value + 1)
      setIndexRevision(value => value + 1)
      setIndexStatus('unavailable')
    }
  }, [])

  const handleIndexBuilt = useCallback(() => {
    setIndexStatus('ready')
    setIndexRevision(value => value + 1)
  }, [])

  const dataBusy = dataStatus === 'checking' || dataStatus === 'uploading'
  const dataActionsAvailable = hasData && !dataBusy
  const indexReady = dataActionsAvailable && indexStatus === 'ready'

  return (
    <main className="min-h-screen px-4 py-8 text-slate-800 sm:px-6 sm:py-12">
      <div className="mx-auto max-w-6xl space-y-8">
        <header className="space-y-3">
          <p className="text-sm font-semibold uppercase tracking-[0.18em] text-indigo-600">Projeto de Banco de Dados</p>
          <div className="max-w-3xl space-y-2">
            <h1 className="text-3xl font-semibold tracking-tight text-slate-900 sm:text-4xl">Índice Hash Estático</h1>
            <p className="text-base leading-7 text-slate-600">
              Carregue os registros, construa o índice e compare o acesso direto com a varredura sequencial.
            </p>
          </div>
        </header>
        <DashboardStatus dataStatus={dataStatus} hasData={hasData} indexStatus={indexStatus} />
        <DataPanel onStateChange={handleDataStateChange} />
        <IndexPanel
          dataAvailable={hasData}
          disabled={dataStatus === 'uploading'}
          key={datasetRevision}
          onIndexBuilt={handleIndexBuilt}
          onIndexStateChange={setIndexStatus}
        />
        <section aria-labelledby="index-tools-heading" className="space-y-4">
          <FlowHeading
            description="Faça uma busca exata ou inspecione como uma chave é distribuída no índice."
            id="index-tools-heading"
            step="3"
            title="Consultar o índice"
          />
          <div className="grid min-w-0 items-start gap-6 xl:grid-cols-2">
            <IndexSearch disabled={!indexReady} key={`${datasetRevision}-${indexRevision}-search`} />
            <HashOverflow disabled={!indexReady} key={`${datasetRevision}-${indexRevision}-hash`} />
          </div>
        </section>
        <ComparisonPanel
          dataAvailable={dataActionsAvailable}
          indexReady={indexReady}
          key={`${datasetRevision}-${indexRevision}`}
        />
      </div>
    </main>
  )
}

function DashboardStatus({ dataStatus, hasData, indexStatus }) {
  let label = 'Verificando dados carregados...'
  let detail = 'Aguarde enquanto consultamos o estado atual da aplicação.'
  let color = 'border-slate-200 bg-white text-slate-700'
  let dot = 'bg-slate-400'

  if (dataStatus === 'uploading') {
    label = 'Arquivo carregando'
    detail = 'O arquivo está sendo processado e dividido em páginas.'
    color = 'border-amber-200 bg-amber-50 text-amber-900'
    dot = 'bg-amber-500'
  } else if (dataStatus === 'error') {
    label = hasData ? 'Erro na última operação; dados anteriores preservados' : 'Erro de carregamento'
    detail = hasData ? 'Você ainda pode trabalhar com o conjunto anterior.' : 'Verifique o backend e tente carregar o arquivo novamente.'
    color = 'border-red-200 bg-red-50 text-red-900'
    dot = 'bg-red-500'
  } else if (!hasData && dataStatus !== 'checking') {
    label = 'Sem arquivo carregado'
    detail = 'Comece selecionando um arquivo TXT com um registro por linha.'
  } else if (indexStatus === 'building') {
    label = 'Índice construindo'
    detail = 'As consultas indexadas serão liberadas ao final da construção.'
    color = 'border-amber-200 bg-amber-50 text-amber-900'
    dot = 'bg-amber-500'
  } else if (indexStatus === 'ready') {
    label = 'Índice pronto'
    detail = 'Todas as consultas e a comparação de custos estão disponíveis.'
    color = 'border-emerald-200 bg-emerald-50 text-emerald-900'
    dot = 'bg-emerald-500'
  } else if (hasData) {
    label = 'Arquivo carregado sem índice'
    detail = 'Construa o índice para liberar a busca indexada e a comparação.'
    color = 'border-blue-200 bg-blue-50 text-blue-900'
    dot = 'bg-blue-500'
  }

  return (
    <div aria-live="polite" className={`flex items-start gap-3 rounded-xl border px-4 py-3.5 ${color}`} role="status">
      <span aria-hidden="true" className={`mt-1.5 size-2.5 shrink-0 rounded-full ${dot}`} />
      <div>
        <p className="text-sm font-semibold">{label}</p>
        <p className="mt-0.5 text-sm opacity-80">{detail}</p>
      </div>
    </div>
  )
}

export default App

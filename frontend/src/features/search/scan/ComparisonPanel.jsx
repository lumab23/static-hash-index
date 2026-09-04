import { useState } from 'react'
import { searchByIndex } from '../index/searchApi.js'
import { compareSearches } from './scanApi.js'

function ComparisonPanel() {
  const [key, setKey] = useState('')
  const [metrics, setMetrics] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleCompare(event) {
    event.preventDefault()

    if (!key.trim()) {
      setError('Informe uma chave para comparar.')
      return
    }

    setLoading(true)
    setError('')
    setMetrics(null)

    try {
      // 1. Chama a API da Luma (Busca Indexada)
      const indexResult = await searchByIndex(key.trim())
      
      // 2. Chama a API da Bianca (Table Scan + Comparação)
      const comparisonResult = await compareSearches(key.trim(), indexResult)
      
      setMetrics(comparisonResult)
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="space-y-6 rounded-2xl bg-slate-900 p-6 text-slate-100 mt-8">
      <div>
        <h2 className="text-xl font-semibold text-purple-400">Table Scan & Comparação</h2>
        <p className="text-sm text-slate-400">
          Compare o custo do Table Scan sequencial com o acesso indexado via Hash.
        </p>
      </div>

      <form className="flex gap-3" onSubmit={handleCompare}>
        <input
          className="min-w-0 flex-1 rounded-lg border border-slate-700 bg-slate-950 px-4 py-2 outline-none focus:border-purple-400"
          onChange={(event) => setKey(event.target.value)}
          placeholder="Digite uma palavra para testar nos dois métodos"
          value={key}
        />
        <button
          className="rounded-lg bg-purple-500 px-4 py-2 font-medium text-slate-50 hover:bg-purple-400 disabled:opacity-50 transition-colors"
          disabled={loading}
          type="submit"
        >
          {loading ? 'Executando...' : 'Comparar Custo'}
        </button>
      </form>

      {error && <p className="text-sm text-red-400">{error}</p>}

      {metrics && (
        <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
          {/* Lado a Lado: Índice vs Scan */}
          <div className="grid gap-6 md:grid-cols-2">
            
            {/* Lado Esquerdo: Busca Indexada */}
            <div className="space-y-4 rounded-xl border border-slate-700 bg-slate-950 p-4">
              <h3 className="font-medium text-cyan-400 text-center">Busca Indexada (Luma)</h3>
              <div className="grid gap-2 grid-cols-2">
                <MetricCard label="Página Acessada" value={metrics.index_search.page_id ?? '-'} />
                <MetricCard label="Páginas Lidas" value={metrics.index_search.pages_read} highlightColor="cyan" />
              </div>
              <p className="text-xs text-slate-400 text-center">
                Tempo: {(metrics.index_search.elapsed_time * 1000).toFixed(4)} ms
              </p>
            </div>

            {/* Lado Direito: Table Scan (Sua parte) */}
            <div className="space-y-4 rounded-xl border border-slate-700 bg-slate-950 p-4">
              <h3 className="font-medium text-purple-400 text-center">Table Scan (Bianca)</h3>
              <div className="grid gap-2 grid-cols-2">
                <MetricCard label="Página Encontrada" value={metrics.table_scan.page_id ?? '-'} />
                <MetricCard label="Páginas Lidas" value={metrics.table_scan.pages_read} highlightColor="purple" />
              </div>
              <p className="text-xs text-slate-400 text-center">
                Tempo: {(metrics.table_scan.elapsed_time * 1000).toFixed(4)} ms
              </p>
            </div>
            
          </div>

          {/* Resumo Final de Economia */}
          <div className="rounded-xl border border-emerald-500/30 bg-emerald-500/10 p-5 text-center">
            <h3 className="text-lg font-semibold text-emerald-400 mb-4">Vantagem do Índice Hash</h3>
            <div className="grid gap-4 sm:grid-cols-3">
              <div>
                <p className="text-xs uppercase text-emerald-400/70">Páginas Economizadas</p>
                <p className="text-2xl font-bold text-emerald-400">+{metrics.pages_saved}</p>
              </div>
              <div>
                <p className="text-xs uppercase text-emerald-400/70">Diferença de Tempo</p>
                <p className="text-2xl font-bold text-emerald-400">{(metrics.time_difference_seconds * 1000).toFixed(2)} ms</p>
              </div>
              <div>
                <p className="text-xs uppercase text-emerald-400/70">Fator de Aceleração</p>
                <p className="text-2xl font-bold text-emerald-400">{metrics.speedup_factor}x</p>
              </div>
            </div>
          </div>
          
          <div className="text-xs text-slate-500 text-center italic">
            Trace do Scan: {metrics.table_scan.trace}
          </div>
        </div>
      )}
    </section>
  )
}

// Componente interno apenas para a organização visual dos cards pequenos
function MetricCard({ label, value, highlightColor }) {
  const borderColor = highlightColor === 'cyan' ? 'border-cyan-400/30' : 
                      highlightColor === 'purple' ? 'border-purple-400/30' : 'border-slate-800'
  
  return (
    <div className={`rounded border bg-slate-900 p-2 text-center ${borderColor}`}>
      <p className="text-[10px] uppercase text-slate-400">{label}</p>
      <p className="mt-1 text-base font-semibold">{value}</p>
    </div>
  )
}

export default ComparisonPanel
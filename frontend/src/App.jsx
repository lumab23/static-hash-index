import IndexSearch from './features/search/index/IndexSearch.jsx'

function App() {
  return (
    <main className="min-h-screen bg-slate-950 px-6 py-12 text-slate-100">
      <div className="mx-auto max-w-4xl space-y-8">
        <h1 className="text-3xl font-semibold">Índice Hash Estático</h1>
        <IndexSearch />
      </div>
    </main>
  )
}

export default App

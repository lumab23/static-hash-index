import { useState } from 'react'

import IndexPanel from './features/index/IndexPanel.jsx'
import HashOverflow from './features/hash/HashOverflow.jsx'
import IndexSearch from './features/search/index/IndexSearch.jsx'

function App() {
  const [indexRevision, setIndexRevision] = useState(0)
  return (
    <main className="min-h-screen bg-slate-950 px-6 py-12 text-slate-100">
      <div className="mx-auto max-w-4xl space-y-8">
        <h1 className="text-3xl font-semibold">Índice Hash Estático</h1>
        <IndexPanel onIndexChanged={() => setIndexRevision(value => value + 1)} />
        <IndexSearch key={indexRevision} />
        <HashOverflow key={indexRevision} />
      </div>
    </main>
  )
}

export default App

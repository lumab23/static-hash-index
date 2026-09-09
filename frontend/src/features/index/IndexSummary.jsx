export default function IndexSummary({ summary }) {
  const cards = [
    ['FR', summary.fr.toLocaleString('pt-BR')],
    ['NB', summary.nb.toLocaleString('pt-BR')],
    ['Total indexado', summary.total_indexed.toLocaleString('pt-BR')],
    ['Tempo de construção', `${(summary.build_time * 1000).toLocaleString('pt-BR', {
      maximumFractionDigits: 4,
    })} ms`],
  ]

  return (
    <dl className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
      {cards.map(([label, value]) => (
        <div className="rounded-lg border border-slate-700 bg-slate-950 p-4" key={label}>
          <dt className="text-sm text-slate-400">{label}</dt>
          <dd className="mt-2 break-words text-xl font-semibold text-cyan-300"
            title={label === 'Tempo de construção' ? `${summary.build_time} segundos` : undefined}>
            {value}
          </dd>
        </div>
      ))}
    </dl>
  )
}

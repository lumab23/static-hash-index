import MetricCard from '../../components/MetricCard.jsx'

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
    <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
      {cards.map(([label, value]) => (
        <MetricCard
          key={label}
          label={label}
          title={label === 'Tempo de construção' ? `${summary.build_time} segundos` : undefined}
          tone="indigo"
          value={value}
        />
      ))}
    </div>
  )
}

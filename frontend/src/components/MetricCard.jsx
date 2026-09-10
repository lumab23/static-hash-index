const toneClasses = {
  default: 'border-slate-200 bg-slate-50 text-slate-900',
  indigo: 'border-indigo-200 bg-indigo-50 text-indigo-900',
  teal: 'border-teal-200 bg-teal-50 text-teal-900',
}

export default function MetricCard({ label, value, tone = 'default', title }) {
  return (
    <div className={`rounded-lg border p-3 ${toneClasses[tone] ?? toneClasses.default}`}>
      <p className="text-xs font-medium uppercase tracking-wide text-slate-500">{label}</p>
      <p className="mt-1 break-words text-lg font-semibold" title={title}>{value}</p>
    </div>
  )
}

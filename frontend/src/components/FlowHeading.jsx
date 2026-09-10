export default function FlowHeading({ description, id, step, title }) {
  return (
    <div className="flex items-start gap-3">
      <span className="flex size-8 shrink-0 items-center justify-center rounded-full bg-indigo-100 text-sm font-semibold text-indigo-700">
        {step}
      </span>
      <div>
        <h2 className="text-xl font-semibold tracking-tight text-slate-900" id={id}>{title}</h2>
        <p className="mt-1 text-sm leading-6 text-slate-600">{description}</p>
      </div>
    </div>
  )
}

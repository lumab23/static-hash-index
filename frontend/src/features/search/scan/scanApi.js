export async function searchByScan(key) {
  const response = await fetch('/api/search/scan', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ key }),
  })

  const body = await response.json()

  if (!response.ok) {
    throw new Error(body.detail || 'Não foi possível realizar o table scan.')
  }

  return body
}

export async function compareSearches(key) {
  const response = await fetch('/api/search/compare', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ key }),
  })

  const body = await response.json()

  if (!response.ok) {
    throw new Error(body.detail || 'Não foi possível realizar a comparação.')
  }

  return body
}

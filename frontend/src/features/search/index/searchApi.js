export async function searchByIndex(key) {
  const response = await fetch('/api/search/index', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ key }),
  })

  const body = await response.json()

  if (!response.ok) {
    throw new Error(body.detail || 'Não foi possível realizar a busca.')
  }

  return body
}

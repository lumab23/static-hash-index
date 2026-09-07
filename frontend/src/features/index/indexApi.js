async function request(path, options = {}) {
  let response
  try {
    response = await fetch(`/api/index${path}`, options)
  } catch {
    throw new Error('Não foi possível conectar à API. Verifique se o backend está em execução.')
  }
  const body = await response.json().catch(() => null)
  if (!response.ok) {
    const detail = body?.detail
    const message = typeof detail === 'string' ? detail
      : response.status === 422 ? 'Confira os valores informados; use números inteiros válidos.'
        : 'Não foi possível concluir a operação. Tente novamente.'
    const error = new Error(message)
    error.status = response.status
    throw error
  }
  return body
}

export function getIndexSummary() {
  return request('/summary')
}

export function buildIndex(fr) {
  return request('/build', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ fr }),
  })
}

export function getIndexBucket(id) {
  return request(`/buckets/${id}`)
}

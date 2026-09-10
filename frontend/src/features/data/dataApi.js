function errorMessage(body, status, fallback) {
  if (typeof body?.detail === 'string') return body.detail
  if (Array.isArray(body?.detail)) {
    return body.detail.map(item => item.msg).filter(Boolean).join(' ') || fallback
  }
  if (status === 413) return 'O arquivo é grande demais para o servidor.'
  return fallback
}

async function request(path, options = {}) {
  let response
  try {
    response = await fetch(`/api${path}`, options)
  } catch (error) {
    if (error.name === 'AbortError') throw error
    throw new Error('Não foi possível conectar à API. Verifique se o backend está em execução.')
  }

  const body = await response.json().catch(() => null)
  if (!response.ok) {
    const error = new Error(errorMessage(
      body,
      response.status,
      'Não foi possível concluir a operação. Tente novamente.',
    ))
    error.status = response.status
    throw error
  }
  return body
}

export function loadData(file, pageSize, signal) {
  const form = new FormData()
  form.append('file', file)
  form.append('page_size', String(pageSize))
  return request('/data/load', { method: 'POST', body: form, signal })
}

export function getPagesSummary(signal) {
  return request('/pages/summary', { signal })
}

export function getPageRecords(pageId, offset = 0, limit = 100, signal) {
  const query = new URLSearchParams({
    offset: String(offset),
    limit: String(limit),
  })
  return request(`/pages/${pageId}/records?${query}`, { signal })
}

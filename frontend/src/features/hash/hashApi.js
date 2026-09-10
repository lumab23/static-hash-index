export async function getHashOverflow(key) {
  let response
  try {
    response = await fetch(`/api/index/hash-overflow?${new URLSearchParams({ key })}`)
  } catch {
    throw new Error('Não foi possível conectar à API. Verifique se o backend está em execução.')
  }
  const body = await response.json().catch(() => null)
  if (!response.ok) {
    throw new Error(typeof body?.detail === 'string' ? body.detail
      : response.status === 422 ? 'Informe uma chave válida.'
        : 'Não foi possível consultar o hash. Tente novamente.')
  }
  return body
}

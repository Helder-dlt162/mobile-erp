const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api'

export async function apiFetch<T>(path: string, token: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, { ...options, headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}`, ...options?.headers } })
  if (!response.ok) {
    const body = await response.json().catch(() => ({})) as { detail?: string }
    throw new Error(body.detail ?? 'Não foi possível concluir a operação')
  }
  if (response.status === 204) return undefined as T
  return response.json() as Promise<T>
}

export { API_URL }

/**
 * FastAPI 統一回應信封 `{ data, error }`（見 backend shared.api.api_wrapper）。
 */
export type ApiEnvelope<T> = {
  data: T | null
  error: { code: string; message: string } | null
}

export function isApiEnvelope(value: unknown): value is ApiEnvelope<unknown> {
  if (value === null || typeof value !== 'object') return false
  const o = value as Record<string, unknown>
  return 'data' in o && 'error' in o
}

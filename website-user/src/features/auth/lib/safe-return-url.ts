/**
 * 僅允許同站台相對導向 /applicant 底下路徑，避免 open redirect。
 */
export function getSafeReturnPath(candidate: string | null | undefined): string | null {
  if (candidate == null || candidate === '') return null
  const t = candidate.trim()
  if (!t.startsWith('/')) return null
  if (t.startsWith('//')) return null
  if (t.includes('://')) return null
  if (!t.startsWith('/applicant')) return null
  return t
}

export function withReturnQuery(loginPath: string, returnPath: string | null): string {
  if (!returnPath) return loginPath
  const safe = getSafeReturnPath(returnPath)
  if (!safe) return loginPath
  const sep = loginPath.includes('?') ? '&' : '?'
  return `${loginPath}${sep}returnUrl=${encodeURIComponent(safe)}`
}

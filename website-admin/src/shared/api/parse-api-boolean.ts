/**
 * 將 API／中介層可能回傳的 boolean、0/1、字串等轉成 boolean。
 * 避免誤用 `Boolean("false") === true`（非空字串為 truthy）。
 *
 * 快取更新：變更成功後可優先 `setQueryData(回傳DTO)` 再 `invalidateQueries`（見 MapImportPage、RuleDetailPage）。
 * 審查／工作流等多以伺服器為準，維持僅 invalidate 即可，除非產品回報畫面未更新。
 */
export function parseApiBoolean(v: unknown): boolean {
  if (v === true || v === 1) return true
  if (v === false || v === 0) return false
  if (typeof v === 'string') {
    const s = v.trim().toLowerCase()
    if (s === 'true' || s === '1') return true
    if (s === 'false' || s === '0' || s === '') return false
  }
  return Boolean(v)
}

/** 自 route-plan / route-preview / review 聚合之 `route_plan` 讀取 snake_case 欄位。 */
export function readOptStr(obj: Record<string, unknown>, key: string): string | undefined {
  const v = obj[key]
  if (v == null || typeof v !== 'string') return undefined
  const s = v.trim()
  return s.length ? s : undefined
}

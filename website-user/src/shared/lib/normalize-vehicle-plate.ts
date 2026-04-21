/**
 * 與後端 `VehiclePlate` 對齊：NFKC、大寫、常見 Unicode 橫線改為 `-`、去除空白。
 * 使用者常貼「ABC–1234」（en dash）或「ABC 1234」。
 */
export function normalizeVehiclePlateInput(s: string): string {
  let t = s.normalize('NFKC').trim().toUpperCase()
  const dashChars = ['\u2013', '\u2014', '\u2212', '\u2010', '\u2011', '\uFE63', '\uFF0D']
  for (const d of dashChars) {
    t = t.split(d).join('-')
  }
  t = t.replace(/\s+/g, '')
  return t
}

/** 後端 `_PLATE_PATTERN` 與一致（正規化後檢查） */
export const VEHICLE_PLATE_NORMALIZED_REGEX = /^[A-Z0-9-]{2,20}$/

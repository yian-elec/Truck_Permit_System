import type { LatLng } from './types'

/** Extract polyline path from route-preview API payload (flexible shapes). */
export function pathsFromRoutePreview(data: unknown): LatLng[] {
  if (!data || typeof data !== 'object') return []
  const d = data as Record<string, unknown>
  const poly = d.polyline ?? d.path ?? d.coordinates
  if (Array.isArray(poly)) {
    return poly
      .map((p) => {
        if (!p || typeof p !== 'object') return null
        const o = p as Record<string, unknown>
        const lat = typeof o.lat === 'number' ? o.lat : Number(o.lat)
        const lng =
          typeof o.lng === 'number' ? o.lng : typeof o.lon === 'number' ? o.lon : Number(o.lng)
        if (!Number.isFinite(lat) || !Number.isFinite(lng)) return null
        return { lat, lng }
      })
      .filter((x): x is LatLng => x !== null)
  }
  return []
}

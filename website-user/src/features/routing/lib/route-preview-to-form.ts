import { VEHICLE_KIND_VALUES } from '@/shared/constants/application-options'
import type { RouteRequestFormValues } from '@/shared/validators/routing'

import type { RoutePreviewData } from '../api/get-route-preview'

/** 與 VEHICLE_KIND_VALUES 一致；表單預設車種為砂石車 */
const DEFAULT_VEHICLE_KIND = 'sand_truck' satisfies RouteRequestFormValues['vehicle_kind']

/**
 * 舊版／車籍 API 與表單代碼不一致時之對照（其餘無法辨識者落回 DEFAULT）。
 * e.g. heavy_truck 僅用於他處，路線表單 enum 不含此值。
 */
const LEGACY_TO_ROUTE_VEHICLE_KIND: Partial<
  Record<string, RouteRequestFormValues['vehicle_kind']>
> = {
  heavy_truck: 'sand_truck',
}

export const ROUTE_REQUEST_FORM_DEFAULTS: RouteRequestFormValues = {
  origin_text: '',
  destination_text: '',
  requested_departure_at: '2026-06-01T08:00:00.000Z',
  vehicle_weight_ton: 15,
  vehicle_kind: DEFAULT_VEHICLE_KIND,
}

function parseWeight(raw: RoutePreviewData['vehicle_weight_ton']): number {
  if (raw == null || raw === '') return ROUTE_REQUEST_FORM_DEFAULTS.vehicle_weight_ton
  const n = typeof raw === 'number' ? raw : Number(String(raw).replace(',', '.'))
  return Number.isFinite(n) && n > 0 ? n : ROUTE_REQUEST_FORM_DEFAULTS.vehicle_weight_ton
}

function parseVehicleKind(raw: string | null | undefined): RouteRequestFormValues['vehicle_kind'] {
  const s = (raw ?? '').trim()
  if (s && VEHICLE_KIND_VALUES.includes(s as (typeof VEHICLE_KIND_VALUES)[number])) {
    return s as RouteRequestFormValues['vehicle_kind']
  }
  if (s && LEGACY_TO_ROUTE_VEHICLE_KIND[s]) {
    return LEGACY_TO_ROUTE_VEHICLE_KIND[s]!
  }
  return DEFAULT_VEHICLE_KIND
}

/** 將 route-preview 資料轉成表單值（供已儲存之路線申請回填）。 */
export function routePreviewToFormValues(p: RoutePreviewData): RouteRequestFormValues {
  const dep = p.requested_departure_at
  let iso = ROUTE_REQUEST_FORM_DEFAULTS.requested_departure_at
  if (dep != null && String(dep).trim() !== '') {
    const d = new Date(String(dep))
    iso = Number.isNaN(d.getTime()) ? String(dep) : d.toISOString()
  }

  return {
    origin_text: p.origin_text,
    destination_text: p.destination_text,
    requested_departure_at: iso,
    vehicle_weight_ton: parseWeight(p.vehicle_weight_ton),
    vehicle_kind: parseVehicleKind(p.vehicle_kind),
  }
}

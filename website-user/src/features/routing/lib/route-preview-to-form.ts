import { VEHICLE_KIND_VALUES } from '@/shared/constants/application-options'
import type { RouteRequestFormValues } from '@/shared/validators/routing'

import type { RoutePreviewData } from '../api/get-route-preview'

export const ROUTE_REQUEST_FORM_DEFAULTS: RouteRequestFormValues = {
  origin_text: '',
  destination_text: '',
  requested_departure_at: '2026-06-01T08:00:00.000Z',
  vehicle_weight_ton: 15,
  vehicle_kind: 'heavy_truck',
}

function parseWeight(raw: RoutePreviewData['vehicle_weight_ton']): number {
  if (raw == null || raw === '') return ROUTE_REQUEST_FORM_DEFAULTS.vehicle_weight_ton
  const n = typeof raw === 'number' ? raw : Number(String(raw).replace(',', '.'))
  return Number.isFinite(n) && n > 0 ? n : ROUTE_REQUEST_FORM_DEFAULTS.vehicle_weight_ton
}

function parseVehicleKind(raw: string | null | undefined): RouteRequestFormValues['vehicle_kind'] {
  if (raw && VEHICLE_KIND_VALUES.includes(raw as (typeof VEHICLE_KIND_VALUES)[number])) {
    return raw as RouteRequestFormValues['vehicle_kind']
  }
  return ROUTE_REQUEST_FORM_DEFAULTS.vehicle_kind
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

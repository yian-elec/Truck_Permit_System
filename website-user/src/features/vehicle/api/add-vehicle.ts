import { z } from 'zod'

import { endpoints } from '@/shared/api/endpoints'
import { post } from '@/shared/api/request'
import { parseApiData } from '@/shared/api/response-parser'
import { normalizeVehiclePlateInput } from '@/shared/lib/normalize-vehicle-plate'
import type { VehicleFormValues } from '@/shared/validators/vehicle'

const schema = z.unknown()

/** 實際送後端的 JSON（勿對 `date | null` 欄位送 `""`，Pydantic 會 422） */
export type VehicleApiPayload = {
  plate_no: string
  vehicle_kind: string
  gross_weight_ton: number
  license_valid_until?: string
  trailer_plate_no?: string
}

export function buildVehicleApiPayload(values: VehicleFormValues): VehicleApiPayload {
  const license = (values.license_valid_until ?? '').trim()
  const licenseDay = license.includes('T') ? license.slice(0, 10) : license
  const trailerRaw = values.trailer_plate_no ?? ''
  const trailerNorm = normalizeVehiclePlateInput(trailerRaw)

  const payload: VehicleApiPayload = {
    plate_no: normalizeVehiclePlateInput(values.plate_no),
    vehicle_kind: values.vehicle_kind,
    gross_weight_ton: values.gross_weight_ton,
  }
  if (licenseDay) payload.license_valid_until = licenseDay
  if (trailerNorm) payload.trailer_plate_no = trailerNorm
  return payload
}

export async function addVehicleApi(applicationId: string, body: VehicleFormValues): Promise<unknown> {
  const { data } = await post<unknown>(endpoints.applicant.vehicles(applicationId), buildVehicleApiPayload(body))
  return parseApiData(schema, data)
}

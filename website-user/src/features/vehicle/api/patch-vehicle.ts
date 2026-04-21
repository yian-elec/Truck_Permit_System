import { z } from 'zod'

import { endpoints } from '@/shared/api/endpoints'
import { patch } from '@/shared/api/request'
import { parseApiData } from '@/shared/api/response-parser'
import type { VehicleFormValues } from '@/shared/validators/vehicle'

import { buildVehicleApiPayload } from './add-vehicle'

const schema = z.unknown()

export async function patchVehicleApi(
  applicationId: string,
  vehicleId: string,
  body: VehicleFormValues,
): Promise<unknown> {
  const { data } = await patch<unknown>(
    endpoints.applicant.vehicle(applicationId, vehicleId),
    buildVehicleApiPayload(body),
  )
  return parseApiData(schema, data)
}

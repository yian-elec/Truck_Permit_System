import { endpoints } from '@/shared/api/endpoints'
import { del } from '@/shared/api/request'

export async function deleteVehicleApi(applicationId: string, vehicleId: string): Promise<void> {
  await del(endpoints.applicant.vehicle(applicationId, vehicleId))
}

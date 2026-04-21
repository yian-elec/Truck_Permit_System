import { endpoints } from '@/shared/api/endpoints'
import { get } from '@/shared/api/request'
import { parseApiData } from '@/shared/api/response-parser'

import {
  applicationDetailSchema,
  type ApplicationDetailDTO,
} from '../types/application-dto.schema'

/** @deprecated Use ApplicationDetailDTO */
export type ApplicationDetailDto = ApplicationDetailDTO

export async function getApplicationDetailApi(applicationId: string): Promise<ApplicationDetailDTO> {
  const { data } = await get<unknown>(endpoints.applicant.applicationDetail(applicationId))
  return parseApiData(applicationDetailSchema, data)
}

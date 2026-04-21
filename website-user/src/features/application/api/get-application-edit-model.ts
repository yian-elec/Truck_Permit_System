import { endpoints } from '@/shared/api/endpoints'
import { get } from '@/shared/api/request'
import { parseApiData } from '@/shared/api/response-parser'

import {
  applicationEditModelSchema,
  type ApplicationEditModelDTO,
} from '../types/application-dto.schema'

export async function getApplicationEditModelApi(applicationId: string): Promise<ApplicationEditModelDTO> {
  const { data } = await get<unknown>(endpoints.applicant.applicationEditModel(applicationId))
  return parseApiData(applicationEditModelSchema, data)
}

import { z } from 'zod'

import { endpoints } from '@/shared/api/endpoints'
import { post } from '@/shared/api/request'
import { parseApiData } from '@/shared/api/response-parser'

const schema = z.unknown()

export async function submitApplicationApi(applicationId: string): Promise<unknown> {
  const { data } = await post<unknown>(endpoints.applicant.submit(applicationId), {})
  return parseApiData(schema, data)
}

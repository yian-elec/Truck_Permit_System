import { z } from 'zod'

import { endpoints } from '@/shared/api/endpoints'
import { get } from '@/shared/api/request'
import { parseApiData } from '@/shared/api/response-parser'
import { pageModelBaseSchema } from '@/shared/types/page-model'

const schema = pageModelBaseSchema

export type ApplicantHomePageModel = z.infer<typeof schema>

export async function getApplicantHomeModelApi(): Promise<ApplicantHomePageModel> {
  const { data } = await get<unknown>(endpoints.pages.applicationHomeModel)
  return parseApiData(schema, data)
}

import { z } from 'zod'

import { endpoints } from '@/shared/api/endpoints'
import { get } from '@/shared/api/request'
import { parseApiData } from '@/shared/api/response-parser'
import { pageModelBaseSchema } from '@/shared/types/page-model'

const schema = pageModelBaseSchema.extend({
  application_id: z.string(),
})

export type ApplicationEditorPageModel = z.infer<typeof schema>

export async function getApplicationEditorModelApi(
  applicationId: string,
  params: Record<string, string | boolean | undefined>,
): Promise<ApplicationEditorPageModel> {
  const search = new URLSearchParams()
  for (const [k, v] of Object.entries(params)) {
    if (v === undefined) continue
    search.set(k, String(v))
  }
  const qs = search.toString()
  const url = `${endpoints.pages.applicationEditorModel(applicationId)}${qs ? `?${qs}` : ''}`
  const { data } = await get<unknown>(url)
  return parseApiData(schema, data)
}

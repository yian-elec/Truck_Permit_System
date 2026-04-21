import { z } from 'zod'

import { endpoints } from '@/shared/api/endpoints'
import { parseApiBoolean } from '@/shared/api/parse-api-boolean'
import { get, post } from '@/shared/api/request'
import { parseResponse } from '@/shared/api/response-parser'

const layerSchema = z.object({
  layer_id: z.string().min(1),
  layer_code: z.string(),
  layer_name: z.string(),
  version_no: z.string(),
  is_active: z.unknown().transform(parseApiBoolean),
  published_at: z.union([z.string(), z.null()]).optional(),
})

export type MapLayerItem = z.infer<typeof layerSchema>

export async function listMapLayers() {
  const { data } = await get<unknown>(endpoints.admin.mapLayers)
  return parseResponse(z.array(layerSchema), data)
}

export async function publishLayer(layerId: string) {
  const { data } = await post<unknown>(endpoints.admin.mapLayerPublish(layerId), {})
  return parseResponse(layerSchema, data)
}

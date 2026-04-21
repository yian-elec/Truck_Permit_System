import { z } from 'zod'

import { ApiError } from './api-error'

export function parseResponse<T>(schema: z.ZodType<T>, data: unknown): T {
  const result = schema.safeParse(data)
  if (!result.success) {
    throw new ApiError({
      message: 'Response validation failed',
      status: 500,
      code: 'PARSE_ERROR',
      details: result.error.flatten(),
    })
  }
  return result.data
}

/**
 * Validates `{ data: T }` API envelope and returns inner `data`.
 */
export function parseApiData<T>(schema: z.ZodType<T>, body: unknown): T {
  const result = z.object({ data: schema }).safeParse(body)
  if (!result.success) {
    throw new ApiError({
      message: 'Invalid API response envelope',
      status: 500,
      code: 'PARSE_ERROR',
      details: result.error.flatten(),
    })
  }
  return result.data.data
}

const envelopeWithNullableData = z.object({
  data: z.unknown().nullable(),
  error: z.unknown().optional().nullable(),
})

/**
 * 與 {@link parseApiData} 相同信封，但允許 `data: null`（後端以空狀態取代 404 時使用）。
 */
export function parseApiDataOrNull<T>(schema: z.ZodType<T>, body: unknown): T | null {
  const envelope = envelopeWithNullableData.safeParse(body)
  if (!envelope.success) {
    throw new ApiError({
      message: 'Invalid API response envelope',
      status: 500,
      code: 'PARSE_ERROR',
      details: envelope.error.flatten(),
    })
  }
  if (envelope.data.error != null) {
    throw new ApiError({
      message: 'Unexpected error envelope',
      status: 500,
      code: 'PARSE_ERROR',
    })
  }
  if (envelope.data.data == null) return null
  return parseResponse(schema, envelope.data.data)
}

import type { z } from 'zod'

import { ApiError } from './api-error'

export function parseResponse<T>(schema: z.ZodType<T>, data: unknown): T {
  const result = schema.safeParse(data)
  if (!result.success) {
    const flat = result.error.flatten()
    const fieldErrors = flat.fieldErrors as Record<string, unknown>
    const firstKey = Object.keys(fieldErrors)[0]
    const firstMsg = firstKey
      ? `${firstKey}: ${JSON.stringify(fieldErrors[firstKey])}`
      : flat.formErrors?.length
        ? JSON.stringify(flat.formErrors)
        : result.error.message
    throw new ApiError({
      message: `Response validation failed (${firstMsg})`,
      status: 500,
      code: 'PARSE_ERROR',
      details: flat,
    })
  }
  return result.data
}

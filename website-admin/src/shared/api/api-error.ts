import axios from 'axios'

export type ApiErrorShape = {
  message: string
  status?: number
  code?: string
  details?: unknown
}

export class ApiError extends Error {
  readonly status?: number
  readonly code?: string
  readonly details?: unknown

  constructor(shape: ApiErrorShape) {
    super(shape.message)
    this.name = 'ApiError'
    this.status = shape.status
    this.code = shape.code
    this.details = shape.details
  }

  static fromUnknown(error: unknown): ApiError {
    if (error instanceof ApiError) return error

    if (axios.isAxiosError(error)) {
      const payload = error.response?.data as
        | { message?: string; code?: string; error?: { message?: string; code?: string } }
        | undefined
      const message =
        payload?.error?.message ??
        payload?.message ??
        error.response?.statusText ??
        error.message ??
        'Request failed'
      return new ApiError({
        message,
        status: error.response?.status,
        code: payload?.error?.code ?? payload?.code ?? error.code,
        details: error.response?.data,
      })
    }

    if (error instanceof Error) {
      return new ApiError({ message: error.message })
    }

    return new ApiError({ message: 'Unknown error' })
  }
}

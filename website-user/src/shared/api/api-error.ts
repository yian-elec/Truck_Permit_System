import axios from 'axios'

export type ApiErrorShape = {
  message: string
  status?: number
  code?: string
  details?: unknown
}

/** 後端 `{ data, error }` 錯誤本體 */
type ApiEnvelopeError = {
  error?: { code?: string; message?: string }
  message?: string
  code?: string
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
      const raw = error.response?.data as ApiEnvelopeError | undefined
      const message =
        raw?.error?.message ??
        raw?.message ??
        error.response?.statusText ??
        error.message ??
        'Request failed'
      const code = raw?.error?.code ?? raw?.code ?? error.code
      return new ApiError({
        message,
        status: error.response?.status,
        code,
        details: error.response?.data,
      })
    }

    if (error instanceof Error) {
      return new ApiError({ message: error.message })
    }

    return new ApiError({ message: 'Unknown error' })
  }
}

/** 供 toast / 內嵌訊息使用 */
export function getErrorMessage(error: unknown): string {
  return ApiError.fromUnknown(error).message
}

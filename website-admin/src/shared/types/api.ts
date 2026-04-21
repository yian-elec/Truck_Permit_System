export type PaginationMeta = {
  page: number
  pageSize: number
  total: number
  totalPages: number
}

export type ApiSuccessResponse<T> = {
  data: T
  meta?: PaginationMeta
}

export type ApiErrorResponse = {
  message: string
  code?: string
  details?: unknown
}

import { z } from 'zod'

import { endpoints } from '@/shared/api/endpoints'
import { get } from '@/shared/api/request'
import { parseResponse } from '@/shared/api/response-parser'

const loose = z.array(z.record(z.string(), z.unknown()))

export async function listOcrJobs() {
  const { data } = await get<unknown>(endpoints.ops.ocrJobs)
  return parseResponse(loose, data)
}

export async function getOcrJob(id: string) {
  const { data } = await get<unknown>(endpoints.ops.ocrJob(id))
  return data as Record<string, unknown>
}

export async function listNotificationJobs() {
  const { data } = await get<unknown>(endpoints.ops.notificationJobs)
  return parseResponse(loose, data)
}

export async function listImportJobs() {
  const { data } = await get<unknown>(endpoints.ops.importJobs)
  return parseResponse(loose, data)
}

export async function getOpsImportJob(id: string) {
  const { data } = await get<unknown>(endpoints.ops.importJob(id))
  return data as Record<string, unknown>
}

export async function listAuditLogs() {
  const { data } = await get<unknown>(endpoints.ops.auditLogs)
  return parseResponse(loose, data)
}

import { z } from 'zod'

import { endpoints } from '@/shared/api/endpoints'
import { get, post } from '@/shared/api/request'
import { parseResponse } from '@/shared/api/response-parser'

const taskSchema = z.object({
  review_task_id: z.string().uuid(),
  application_id: z.string().uuid(),
  stage: z.string(),
  status: z.string(),
  assignee_user_id: z.string().uuid().nullable().optional(),
  due_at: z.string().nullable().optional(),
  created_at: z.string(),
  updated_at: z.string(),
})

const taskListSchema = z.array(taskSchema)

export type ReviewTaskSummary = z.infer<typeof taskSchema>

export async function listReviewTasks(params: { limit: number; offset: number }) {
  const { data } = await get<unknown>(endpoints.review.tasks, {
    params: { limit: params.limit, offset: params.offset },
  })
  return parseResponse(taskListSchema, data)
}

const assignOutSchema = z.object({
  review_task_id: z.string().uuid(),
  assignee_user_id: z.string().uuid(),
  status: z.string(),
})

export async function assignReviewTask(applicationId: string, assigneeUserId: string) {
  const { data } = await post<unknown>(endpoints.review.assign(applicationId), {
    assignee_user_id: assigneeUserId,
  })
  return parseResponse(assignOutSchema, data)
}

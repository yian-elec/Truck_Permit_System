import { z } from 'zod'

import { endpoints } from '@/shared/api/endpoints'
import { get, post } from '@/shared/api/request'
import { parseResponse } from '@/shared/api/response-parser'

const commentSchema = z.object({
  comment_id: z.string().uuid(),
  application_id: z.string().uuid(),
  comment_type: z.string(),
  content: z.string(),
  created_by: z.string().uuid(),
  created_at: z.string(),
})

export type CommentSummary = z.infer<typeof commentSchema>

export async function listComments(applicationId: string) {
  const { data } = await get<unknown>(endpoints.review.comments(applicationId))
  return parseResponse(z.array(commentSchema), data)
}

export async function postComment(applicationId: string, body: { comment_type: string; content: string }) {
  const { data } = await post<unknown>(endpoints.review.comments(applicationId), body)
  return parseResponse(commentSchema, data)
}

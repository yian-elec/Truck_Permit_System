import { z } from 'zod'

import { endpoints } from '@/shared/api/endpoints'
import { parseApiBoolean } from '@/shared/api/parse-api-boolean'
import { get, patch, post } from '@/shared/api/request'
import { parseResponse } from '@/shared/api/response-parser'

const listItemSchema = z.object({
  // 後端為 UUID 字串；避免 z.string().uuid() 與部分版本／格式不相容
  rule_id: z.string().min(1),
  layer_id: z.string().min(1),
  rule_name: z.string(),
  rule_type: z.string(),
  weight_limit_ton: z.union([z.string(), z.number()]).nullable().optional(),
  // JSON 有時會出現字串數字（中介或序列化）
  priority: z.coerce.number(),
  is_active: z.unknown().transform(parseApiBoolean),
  updated_at: z.string(),
})

const detailSchema = listItemSchema.extend({
  direction: z.string().nullable().optional(),
  time_rule_text: z.string().nullable().optional(),
  effective_from: z.string().nullable().optional(),
  effective_to: z.string().nullable().optional(),
  created_at: z.string(),
})

export type RuleListItem = z.infer<typeof listItemSchema>
export type RuleDetail = z.infer<typeof detailSchema>

export async function listRules(params: { layer_id?: string; is_active?: boolean }) {
  const { data } = await get<unknown>(endpoints.admin.restrictionsRules, { params })
  return parseResponse(z.array(listItemSchema), data)
}

export async function getRule(ruleId: string) {
  const { data } = await get<unknown>(endpoints.admin.restrictionRule(ruleId))
  return parseResponse(detailSchema, data)
}

export async function createRule(body: Record<string, unknown>) {
  const { data } = await post<unknown>(endpoints.admin.restrictionsRules, body)
  return parseResponse(detailSchema, data)
}

export async function patchRule(ruleId: string, body: Record<string, unknown>) {
  const { data } = await patch<unknown>(endpoints.admin.restrictionRule(ruleId), body)
  return parseResponse(detailSchema, data)
}

export async function activateRule(ruleId: string) {
  const { data } = await post<unknown>(endpoints.admin.restrictionRuleActivate(ruleId), {})
  return parseResponse(detailSchema, data)
}

export async function deactivateRule(ruleId: string) {
  const { data } = await post<unknown>(endpoints.admin.restrictionRuleDeactivate(ruleId), {})
  return parseResponse(detailSchema, data)
}

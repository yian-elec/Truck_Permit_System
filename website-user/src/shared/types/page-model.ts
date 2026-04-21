import { z } from 'zod'

export const pageSectionSchema = z.object({
  section_code: z.string(),
  sort_order: z.number(),
  is_required_for_render: z.boolean(),
})

export const pageModelBaseSchema = z.object({
  page_kind: z.string(),
  contract_version_major: z.number(),
  sections: z.array(pageSectionSchema),
  payload_by_section: z.record(z.string(), z.unknown()),
})

export type PageSection = z.infer<typeof pageSectionSchema>
export type PageModelBase = z.infer<typeof pageModelBaseSchema>

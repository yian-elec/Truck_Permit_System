export type PageSectionItem = {
  section_code: string
  sort_order: number
  is_required_for_render: boolean
  feed_roles: string[]
  prerequisite_section_codes: string[]
}

export type PageModelResult = {
  page_kind: string
  contract_version_major: number
  application_id: string | null
  sections: PageSectionItem[]
  payload_by_section: Record<string, unknown>
}

export type ServiceOverview = {
  service_code: string
  display_name: string
  description: string
  api_version: string
}

export type RequiredDocumentsPayload = {
  documents: { id?: string; title?: string; description?: string }[]
}

export type HandlingUnitsPayload = {
  units: { name?: string; phone?: string; address?: string }[]
}

export type ConsentLatest = {
  version: string
  effective_at: string
  summary: string
  must_accept_before_submit: boolean
}

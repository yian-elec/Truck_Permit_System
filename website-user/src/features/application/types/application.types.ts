export type ApplicationStatus = string

export type { ApplicationDetailDTO, ApplicationEditModelDTO } from './application-dto.schema'

/** @deprecated Use ApplicationDetailDTO from application-dto.schema */
export type ApplicationDetail = {
  application_id: string
  application_no: string
  status: ApplicationStatus
  updated_at: string
  [key: string]: unknown
}

export type ApplicationEditModel = Record<string, unknown>

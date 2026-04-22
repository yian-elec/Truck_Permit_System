import { routePaths } from '@/shared/constants/route-paths'

export const MISSING_REASON_MESSAGES: Record<string, string> = {
  incomplete_profile: '尚未完成申請人資料',
  missing_consent: '尚未完成申辦同意書',
  missing_vehicles: '尚未新增車輛資料',
  missing_required_attachments: '尚未上傳必備附件',
  permit_period_exceeds_policy: '許可期間超過法規或政策允許天數，請修正',
  incomplete_route: '尚未完成路線資料',
}

export const SECTION_ANCHOR_IDS = {
  core: 'section-application-core',
  vehicles: 'section-vehicles',
  attachments: 'section-attachments',
  route: 'section-route',
  consent: 'section-consent',
} as const

export function missingReasonToMessage(code: string): string {
  return MISSING_REASON_MESSAGES[code] ?? code.replace(/_/g, ' ')
}

/**
 * 返回編輯頁內可捲動之錨點；`missing_consent` 指向申辦同意書區（可於該處或預覽頁寫入紀錄）。
 */
export function missingReasonToEditHash(code: string): string | null {
  const id = applicationIdForEditHash(code)
  if (!id) return null
  return `#${id}`
}

function applicationIdForEditHash(code: string): string | null {
  switch (code) {
    case 'incomplete_profile':
      return SECTION_ANCHOR_IDS.core
    case 'missing_vehicles':
      return SECTION_ANCHOR_IDS.vehicles
    case 'missing_required_attachments':
      return SECTION_ANCHOR_IDS.attachments
    case 'incomplete_route':
    case 'permit_period_exceeds_policy':
      return code === 'incomplete_route' ? SECTION_ANCHOR_IDS.route : SECTION_ANCHOR_IDS.core
    case 'missing_consent':
      return SECTION_ANCHOR_IDS.consent
    default:
      return null
  }
}

export function buildEditWithMissingHash(applicationId: string, code: string): string | null {
  const h = missingReasonToEditHash(code)
  if (!h) {
    return null
  }
  return `${routePaths.applicantApplicationEdit(applicationId)}${h}`
}

const PREVIEW_ANCHOR_BY_CODE: Record<string, string> = {
  missing_consent: 'section-preview-consent',
  incomplete_profile: 'section-preview-applicant',
  missing_vehicles: 'section-preview-vehicles',
  missing_required_attachments: 'section-preview-attachments',
  incomplete_route: 'section-preview-route',
  permit_period_exceeds_policy: 'section-preview-core',
}

/**
 * 依目前頁面決定「前往補填」導向；路徑相同則只捲到錨點不換頁。
 * - 編輯頁：/edit#section-…（可編輯處補正）
 * - 預覽頁：/edit/preview#section-preview-…（先捲到對應說明區，實際修改請用「返回編輯」）
 */
export function getMissingItemActionHref(
  applicationId: string,
  code: string,
  page: 'edit' | 'preview',
): string | null {
  if (page === 'preview') {
    const id = PREVIEW_ANCHOR_BY_CODE[code]
    if (id) {
      return `${routePaths.applicantApplicationEditPreview(applicationId)}#${id}`
    }
  }
  return buildEditWithMissingHash(applicationId, code)
}

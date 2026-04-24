/**
 * 後台「操作者語意」用語，避免主要畫面出現純工程狀態字串。
 * 未列名者仍顯示原值，必要時在進階區檢視。
 */

const STATUS_PRETTY: Record<string, string> = {
  // 審查／案件常見
  initial: '等待處理',
  pending: '等待處理',
  pending_assignment: '等待分派',
  in_review: '審核中',
  open: '待處理',
  submitted: '已送出',
  closed: '已結案',
  succeeded: '已完成',
  success: '已完成',
  failed: '失敗，需處理',
  error: '失敗，需處理',
  running: '處理中',
  cancelled: '已取消',
  draft: '草稿',
  approved: '已核准',
  rejected: '已駁回',
  active: '使用中',
  inactive: '未使用',
}

const STAGE_PRETTY: Record<string, string> = {
  initial: '新進件',
  review: '審核中',
  supplement: '補件中',
  closed: '已結案',
}

export function formatOperatorStatus(status: string): string {
  if (!status) return '—'
  const k = status.toLowerCase().replace(/\s+/g, '_')
  return STATUS_PRETTY[k] ?? status
}

export function formatOperatorStage(stage: string): string {
  if (!stage) return '—'
  const k = stage.toLowerCase()
  return STAGE_PRETTY[k] ?? stage
}

/** 工作中心列表（匯入／OCR 等列）的狀態欄顯示 */
export function formatJobListStatus(status: string): string {
  return formatOperatorStatus(status)
}

/** 優先級：數值越大越優先（給審查員的提示用） */
export function formatRulePriority(priority: number): { level: '高' | '中' | '低'; hint: string } {
  if (priority >= 80) return { level: '高', hint: '數值越大，越先套用' }
  if (priority >= 40) return { level: '中', hint: '數值越大，越先套用' }
  return { level: '低', hint: '數值越大，越先套用' }
}

const PERMISSION_PRETTY: Record<string, string> = {
  'iam.assign_roles': '可管理角色與權限',
  'iam.view_self': '可查看自己的帳號與權限',
  'review.task.assign': '可分派審查案件',
  'review.case.read': '可檢視審查案件內容',
  'admin.ops.read': '可檢視作業與匯入紀錄',
}

export function formatPermissionLabel(code: string): string {
  return PERMISSION_PRETTY[code] ?? code
}

export const REJECT_REASON_PRESETS: { value: string; label: string }[] = [
  { value: 'documents', label: '文件不完整' },
  { value: 'route', label: '路線不符合規定' },
  { value: 'data', label: '申請資料有誤' },
  { value: 'other', label: '其他' },
]

export const SUPPLEMENT_MESSAGE_TEMPLATES: string[] = [
  '請補上有效行照影本（須在檢驗效期內）。',
  '請重新上傳清晰、可辨識之車輛證明文件全頁。',
  '請補充工程合約、施工或通行原因之說明文件。',
  '請補上棄土場同意書與相關流向證明。',
]

const ROLE_CHOICES: { value: string; label: string }[] = [
  { value: 'admin', label: '後台管理員' },
  { value: 'review_officer', label: '審查人員' },
  { value: 'map_editor', label: '圖資管理員' },
  { value: 'viewer', label: '只讀查詢' },
]

export function getRoleSelectOptions() {
  return ROLE_CHOICES
}

/** 審查列表從 case API 讀到之 application 彙整 */
export function pickPrimaryPlate(vehicles: Record<string, unknown>[]): string {
  const v0 = vehicles[0]
  if (!v0) return '—'
  return String(v0.plate_no ?? v0.vehicle_id ?? '—')
}

export function pickApplicantName(application: Record<string, unknown>): string {
  const ap = application.applicant as Record<string, unknown> | undefined
  const co = application.company as Record<string, unknown> | undefined
  if (ap?.name) return String(ap.name)
  if (co?.company_name) return String(co.company_name)
  return '—'
}

/** 從審查案件回傳的 application 物件整理列表欄位用；日期請傳入月/日短格式化函式。 */
export function summarizeApplicationForTaskList(
  application: Record<string, unknown> | undefined,
  formatDateShort: (iso: string) => string = (iso) => {
    const d = new Date(iso)
    if (Number.isNaN(d.getTime())) return '—'
    return `${d.getMonth() + 1}/${d.getDate()}`
  },
): {
  applicationNo: string
  applicantName: string
  plate: string
  periodLabel: string
} {
  if (!application) {
    return { applicationNo: '—', applicantName: '—', plate: '—', periodLabel: '—' }
  }
  const vehicles = (application.vehicles as Record<string, unknown>[] | undefined) ?? []
  const start = application.requested_start_at ? String(application.requested_start_at) : ''
  const end = application.requested_end_at ? String(application.requested_end_at) : ''
  let periodLabel = '—'
  if (start && end) {
    periodLabel = `${formatDateShort(start)}–${formatDateShort(end)}`
  } else if (start) {
    periodLabel = formatDateShort(start)
  }
  return {
    applicationNo: String(application.application_no ?? '—'),
    applicantName: pickApplicantName(application),
    plate: pickPrimaryPlate(vehicles),
    periodLabel,
  }
}

/** 不顯示在「操作紀錄」摘要的技術/系統事件 */
export function isNoiseAuditActionCode(code: string | undefined | null): boolean {
  if (!code) return false
  const t = String(code).toLowerCase()
  if (t.includes('ops.seed') || t.includes('bootstrap')) return true
  if (t.includes('page model') || t.includes('pagemodel')) return true
  return false
}

/** 圖資匯入列表「作業類型」欄白話化（仍保留原始字串於 title 需要時可再展開） */
export function formatImportJobTypeForList(jobType: string): string {
  const t = jobType.trim().toLowerCase()
  if (!t) return '—'
  if (t.includes('kml')) return 'KML 圖資上傳'
  if (t.includes('layer') || t.includes('map') || t.includes('gis')) return '圖資匯入'
  return jobType
}

/** 稽核「操作」欄：降低工程代碼感；系統雜訊合併為白話 */
export function formatAuditActionForList(code: string | undefined | null): string {
  if (!code) return '—'
  if (isNoiseAuditActionCode(code)) return '系統作業'
  return String(code).replace(/\./g, ' › ')
}

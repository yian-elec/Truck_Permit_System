export const routePaths = {
  home: '/',
  login: '/login',
  mfa: '/mfa',
  adminHome: '/admin',
  /** 作業中心：申請審核、文件辨識、通知、圖資匯入（不含全站操作紀錄） */
  workCenter: '/admin/work',
  /** 全站操作／稽核紀錄（與作業中心分頁分開） */
  auditLog: '/admin/audit-log',
  /** 舊連結；請改用 workCenter + ?tab= */
  reviewTasks: '/admin/review/tasks',
  reviewCase: (id: string) => `/admin/review/applications/${id}`,
  reviewRoute: (id: string) => `/admin/review/applications/${id}/route`,
  ruleList: '/admin/restrictions/rules',
  ruleDetail: (id: string) => `/admin/restrictions/rules/${id}`,
  mapLayers: '/admin/map-layers',
  mapImports: '/admin/map-imports',
  /** 舊連結；請改用 workCenter?tab=ocr 等 */
  ops: '/admin/ops',
  userRoles: (id: string) => `/admin/users/${id}/roles`,
} as const

export function workCenterUrl(tab: 'review' | 'ocr' | 'notif' | 'import' = 'review') {
  return `${routePaths.workCenter}?tab=${tab}` as const
}

export type RoutePath = (typeof routePaths)[keyof typeof routePaths]

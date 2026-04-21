export const routePaths = {
  home: '/',
  login: '/login',
  mfa: '/mfa',
  adminHome: '/admin',
  reviewTasks: '/admin/review/tasks',
  reviewCase: (id: string) => `/admin/review/applications/${id}`,
  reviewRoute: (id: string) => `/admin/review/applications/${id}/route`,
  ruleList: '/admin/restrictions/rules',
  ruleDetail: (id: string) => `/admin/restrictions/rules/${id}`,
  mapLayers: '/admin/map-layers',
  mapImports: '/admin/map-imports',
  ops: '/admin/ops',
  userRoles: (id: string) => `/admin/users/${id}/roles`,
} as const

export type RoutePath = (typeof routePaths)[keyof typeof routePaths]

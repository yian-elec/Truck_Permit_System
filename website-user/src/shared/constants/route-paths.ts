export const routePaths = {
  home: '/',
  consent: '/consent',
  login: '/login',
  register: '/register',
  mfa: '/mfa',
  applicant: '/applicant',
  applicantApplicationNew: '/applicant/applications/new',
  applicantApplication: (applicationId: string) => `/applicant/applications/${applicationId}`,
  applicantApplicationEdit: (applicationId: string) =>
    `/applicant/applications/${applicationId}/edit`,
  applicantApplicationEditPreview: (applicationId: string) =>
    `/applicant/applications/${applicationId}/edit/preview`,
  applicantApplicationSubmitComplete: (applicationId: string) =>
    `/applicant/applications/${applicationId}/submit-complete`,
  applicantApplicationSupplement: (applicationId: string) =>
    `/applicant/applications/${applicationId}/supplement`,
  applicantApplicationPermit: (applicationId: string) =>
    `/applicant/applications/${applicationId}/permit`,
} as const

export type RoutePath = (typeof routePaths)[keyof typeof routePaths]

export const endpoints = {
  auth: {
    register: '/api/v1/auth/register',
    login: '/api/v1/auth/login',
    verifyMfa: '/api/v1/auth/mfa/verify',
    refresh: '/api/v1/auth/refresh',
    logout: '/api/v1/auth/logout',
    me: '/api/v1/auth/me',
    permissions: '/api/v1/auth/me/permissions',
  },
  publicService: {
    overview: '/api/v1/public/services/heavy-truck-permit',
    consentLatest: '/api/v1/public/services/heavy-truck-permit/consent/latest',
    requiredDocuments: '/api/v1/public/services/heavy-truck-permit/required-documents',
    handlingUnits: '/api/v1/public/services/heavy-truck-permit/handling-units',
  },
  applicant: {
    applications: '/api/v1/applicant/applications',
    applicationDetail: (id: string) => `/api/v1/applicant/applications/${id}`,
    applicationEditModel: (id: string) => `/api/v1/applicant/applications/${id}/edit-model`,
    applicationConsent: (id: string) => `/api/v1/applicant/applications/${id}/consent`,
    applicationTimeline: (id: string) => `/api/v1/applicant/applications/${id}/timeline`,
    submissionCheck: (id: string) => `/api/v1/applicant/applications/${id}/submission-check`,
    submit: (id: string) => `/api/v1/applicant/applications/${id}/submit`,
    supplementRequests: (id: string) => `/api/v1/applicant/applications/${id}/supplement-requests`,
    supplementResponse: (id: string) => `/api/v1/applicant/applications/${id}/supplement-response`,
    permit: (id: string) => `/api/v1/applicant/applications/${id}/permit`,
    permitDownloadUrl: (id: string) => `/api/v1/applicant/applications/${id}/permit/download-url`,
    vehicles: (applicationId: string) => `/api/v1/applicant/applications/${applicationId}/vehicles`,
    vehicle: (applicationId: string, vehicleId: string) =>
      `/api/v1/applicant/applications/${applicationId}/vehicles/${vehicleId}`,
    attachmentsUploadUrl: (applicationId: string) =>
      `/api/v1/applicant/applications/${applicationId}/attachments/upload-url`,
    attachmentsComplete: (applicationId: string) =>
      `/api/v1/applicant/applications/${applicationId}/attachments/complete`,
    attachments: (applicationId: string) =>
      `/api/v1/applicant/applications/${applicationId}/attachments`,
    attachment: (applicationId: string, attachmentId: string) =>
      `/api/v1/applicant/applications/${applicationId}/attachments/${attachmentId}`,
    attachmentDownloadUrl: (applicationId: string, attachmentId: string) =>
      `/api/v1/applicant/applications/${applicationId}/attachments/${attachmentId}/download-url`,
    routeRequest: (applicationId: string) =>
      `/api/v1/applicant/applications/${applicationId}/route-request`,
    routeRequestReplan: (applicationId: string) =>
      `/api/v1/applicant/applications/${applicationId}/route-request/replan`,
    routePreview: (applicationId: string) =>
      `/api/v1/applicant/applications/${applicationId}/route-preview`,
  },
  pages: {
    applicationEditorModel: (applicationId: string) =>
      `/api/v1/applicant/pages/applications/${applicationId}/editor-model`,
  },
} as const

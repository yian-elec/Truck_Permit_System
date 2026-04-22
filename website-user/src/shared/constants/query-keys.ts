export const queryKeys = {
  auth: {
    me: ['auth', 'me'] as const,
    permissions: ['auth', 'permissions'] as const,
  },
  publicService: {
    overview: ['public-service', 'overview'] as const,
    consentLatest: ['public-service', 'consent-latest'] as const,
    requiredDocuments: ['public-service', 'required-documents'] as const,
    handlingUnits: ['public-service', 'handling-units'] as const,
  },
  pageModel: {
    applicationEditor: (applicationId: string) =>
      ['page-model', 'application-editor', applicationId] as const,
  },
  applicant: {
    applications: ['applicant', 'applications'] as const,
    applicationDetail: (id: string) => ['applicant', 'application', id] as const,
    applicationEditModel: (id: string) => ['applicant', 'application', id, 'edit-model'] as const,
    applicationTimeline: (id: string) => ['applicant', 'application', id, 'timeline'] as const,
    submissionCheck: (id: string) => ['applicant', 'application', id, 'submission-check'] as const,
    submission: (id: string) => ['applicant', 'application', id, 'submission'] as const,
    supplementRequests: (id: string) => ['applicant', 'application', id, 'supplement-requests'] as const,
    permit: (id: string) => ['applicant', 'application', id, 'permit'] as const,
    vehicles: (applicationId: string) => ['applicant', 'application', applicationId, 'vehicles'] as const,
    attachments: (applicationId: string) =>
      ['applicant', 'application', applicationId, 'attachments'] as const,
    attachment: (applicationId: string, attachmentId: string) =>
      ['applicant', 'application', applicationId, 'attachments', attachmentId] as const,
    routePreview: (applicationId: string) =>
      ['applicant', 'application', applicationId, 'route-preview'] as const,
  },
} as const

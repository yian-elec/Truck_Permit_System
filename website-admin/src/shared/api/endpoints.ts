const v1 = '/api/v1'

export const endpoints = {
  auth: {
    login: `${v1}/auth/login`,
    logout: `${v1}/auth/logout`,
    me: `${v1}/auth/me`,
    permissions: `${v1}/auth/me/permissions`,
    mfaVerify: `${v1}/auth/mfa/verify`,
  },
  review: {
    tasks: `${v1}/review/tasks`,
    dashboard: `${v1}/review/dashboard`,
    application: (applicationId: string) => `${v1}/review/applications/${applicationId}`,
    assign: (applicationId: string) => `${v1}/review/applications/${applicationId}/assign`,
    comments: (applicationId: string) => `${v1}/review/applications/${applicationId}/comments`,
    ocrSummary: (applicationId: string) => `${v1}/review/applications/${applicationId}/ocr-summary`,
    attachmentPreview: (applicationId: string, attachmentId: string) =>
      `${v1}/review/applications/${applicationId}/attachments/${attachmentId}/preview`,
    decisions: (applicationId: string) => `${v1}/review/applications/${applicationId}/decisions`,
    auditTrail: (applicationId: string) => `${v1}/review/applications/${applicationId}/audit-trail`,
    supplement: (applicationId: string) => `${v1}/review/applications/${applicationId}/supplement`,
    approve: (applicationId: string) => `${v1}/review/applications/${applicationId}/approve`,
    reject: (applicationId: string) => `${v1}/review/applications/${applicationId}/reject`,
    routePreview: (applicationId: string) => `${v1}/review/applications/${applicationId}/route-preview`,
    routePlan: (applicationId: string) => `${v1}/review/applications/${applicationId}/route-plan`,
    routePlanRuleHits: (applicationId: string) =>
      `${v1}/review/applications/${applicationId}/route-plan/rule-hits`,
    routePlanSelectCandidate: (applicationId: string) =>
      `${v1}/review/applications/${applicationId}/route-plan/select-candidate`,
    routePlanPatchItinerary: (applicationId: string) =>
      `${v1}/review/applications/${applicationId}/route-plan/patch-itinerary`,
    routePlanOverride: (applicationId: string) =>
      `${v1}/review/applications/${applicationId}/route-plan/override`,
    routePlanReplan: (applicationId: string) =>
      `${v1}/review/applications/${applicationId}/route-plan/replan`,
  },
  pageModel: {
    reviewApplication: (applicationId: string) =>
      `${v1}/review/pages/applications/${applicationId}/review-model`,
    adminDashboard: `${v1}/admin/pages/dashboard-model`,
  },
  admin: {
    restrictionsRules: `${v1}/admin/restrictions/rules`,
    restrictionRule: (ruleId: string) => `${v1}/admin/restrictions/rules/${ruleId}`,
    restrictionRuleActivate: (ruleId: string) => `${v1}/admin/restrictions/rules/${ruleId}/activate`,
    restrictionRuleDeactivate: (ruleId: string) => `${v1}/admin/restrictions/rules/${ruleId}/deactivate`,
    mapLayers: `${v1}/admin/map-layers`,
    mapLayerPublish: (layerId: string) => `${v1}/admin/map-layers/${layerId}/publish`,
    mapImportsKml: `${v1}/admin/map-imports/kml`,
    mapImportJob: (importJobId: string) => `${v1}/admin/map-imports/${importJobId}`,
    userRoles: (userId: string) => `${v1}/admin/users/${userId}/roles`,
  },
  ops: {
    ocrJobs: `${v1}/ops/ocr-jobs`,
    ocrJob: (ocrJobId: string) => `${v1}/ops/ocr-jobs/${ocrJobId}`,
    notificationJobs: `${v1}/ops/notification-jobs`,
    importJobs: `${v1}/ops/import-jobs`,
    importJob: (importJobId: string) => `${v1}/ops/import-jobs/${importJobId}`,
    auditLogs: `${v1}/ops/audit-logs`,
  },
} as const

const labels: Record<string, string> = {
  draft: '草稿',
  submitted: '已送件',
  under_review: '審核中',
  approved: '核准',
  rejected: '駁回',
  supplement_required: '待補件',
}

export function formatApplicationStatus(status: string): string {
  return labels[status] ?? status.replace(/_/g, ' ')
}

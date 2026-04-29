const labels: Record<string, string> = {
  draft: '草稿',
  submitted: '已送出',
  under_review: '審核中',
  approved: '核准',
  rejected: '駁回',
  supplement_required: '補件中',
  resubmitted: '等待處理',
  cancelled: '已取消',
  withdrawn: '已撤回',
}

/** 我的案件列表「依狀態篩選」：第一項為全部，其餘為後端可能回傳之 status。 */
export const APPLICATION_LIST_STATUS_FILTER_OPTIONS: { value: string; label: string }[] = [
  { value: '', label: '全部' },
  ...(
    [
      'draft',
      'submitted',
      'supplement_required',
      'resubmitted',
      'under_review',
      'approved',
      'rejected',
      'cancelled',
      'withdrawn',
    ] as const
  ).map((value) => ({ value, label: labels[value] })),
]

export function formatApplicationStatus(status: string): string {
  return labels[status] ?? status.replace(/_/g, ' ')
}

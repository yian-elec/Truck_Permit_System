/**
 * 申請端「案件內容編輯」(/edit) 僅在草稿與待補件階段開放；已送件未待補件則導回詳情。
 */
const APPLICANT_EDITABLE: ReadonlySet<string> = new Set(['draft', 'supplement_required'])

export function isApplicantApplicationEditableStatus(status: string | undefined | null): boolean {
  if (status == null || status === '') return false
  return APPLICANT_EDITABLE.has(status)
}

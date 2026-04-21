import { useQuery } from '@tanstack/react-query'

import { queryKeys } from '@/shared/constants/query-keys'

import { getApplicationEditorModelApi } from '../api/get-application-editor-model'

export function useApplicationEditorPageModel(
  applicationId: string | undefined,
  params: Record<string, string | boolean | undefined> = {},
  /** 若為 false，不發送請求（例如案件明細尚未載入） */
  queryEnabled = true,
) {
  return useQuery({
    queryKey: [...queryKeys.pageModel.applicationEditor(applicationId ?? ''), params] as const,
    queryFn: () => getApplicationEditorModelApi(applicationId!, params),
    enabled: Boolean(applicationId) && queryEnabled,
  })
}

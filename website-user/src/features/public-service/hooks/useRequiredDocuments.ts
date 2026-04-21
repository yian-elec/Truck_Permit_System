import { useQuery } from '@tanstack/react-query'

import { queryKeys } from '@/shared/constants/query-keys'

import { getRequiredDocumentsApi } from '../api/get-required-documents'

export function useRequiredDocuments() {
  return useQuery({
    queryKey: queryKeys.publicService.requiredDocuments,
    queryFn: getRequiredDocumentsApi,
  })
}

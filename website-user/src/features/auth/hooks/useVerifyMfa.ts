import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate, useSearchParams } from 'react-router-dom'

import { routePaths } from '@/shared/constants/route-paths'
import { queryKeys } from '@/shared/constants/query-keys'

import { getSafeReturnPath } from '../lib/safe-return-url'
import { verifyMfaApi } from '../api/verify-mfa'
import { useAuthStore } from '../store/auth.store'

export function useVerifyMfa() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const queryClient = useQueryClient()
  const setSession = useAuthStore((s) => s.setSession)
  const returnPath = getSafeReturnPath(searchParams.get('returnUrl'))

  return useMutation({
    mutationFn: verifyMfaApi,
    onSuccess: (data) => {
      setSession(data.access_token, null)
      void queryClient.invalidateQueries({ queryKey: queryKeys.auth.me })
      navigate(returnPath ?? routePaths.applicant, { replace: true })
    },
  })
}

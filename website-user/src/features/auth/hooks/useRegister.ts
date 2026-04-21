import { useMutation } from '@tanstack/react-query'

import { registerApi } from '../api/register'

export function useRegister() {
  return useMutation({
    mutationFn: registerApi,
  })
}

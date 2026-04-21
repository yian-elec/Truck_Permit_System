import { useMutation, useQueryClient } from '@tanstack/react-query'

import { queryKeys } from '@/shared/constants/query-keys'

import type { VehicleFormValues } from '@/shared/validators/vehicle'

import { addVehicleApi } from '../api/add-vehicle'

export function useAddVehicle(applicationId: string | undefined) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (body: VehicleFormValues) => addVehicleApi(applicationId!, body),
    onSuccess: () => {
      if (!applicationId) return
      void queryClient.invalidateQueries({
        queryKey: queryKeys.applicant.applicationEditModel(applicationId),
      })
      void queryClient.invalidateQueries({
        queryKey: queryKeys.applicant.applicationDetail(applicationId),
      })
    },
  })
}

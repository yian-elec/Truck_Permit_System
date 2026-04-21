import { useMutation, useQueryClient } from '@tanstack/react-query'

import { queryKeys } from '@/shared/constants/query-keys'

import type { VehicleFormValues } from '@/shared/validators/vehicle'

import { patchVehicleApi } from '../api/patch-vehicle'

export function usePatchVehicle(applicationId: string | undefined) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ vehicleId, body }: { vehicleId: string; body: VehicleFormValues }) =>
      patchVehicleApi(applicationId!, vehicleId, body),
    onSuccess: () => {
      if (!applicationId) return
      void queryClient.invalidateQueries({
        queryKey: queryKeys.applicant.applicationEditModel(applicationId),
      })
    },
  })
}

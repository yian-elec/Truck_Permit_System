import { useMutation, useQueryClient } from '@tanstack/react-query'

import { queryKeys } from '@/shared/constants/query-keys'

import { deleteVehicleApi } from '../api/delete-vehicle'

export function useDeleteVehicle(applicationId: string | undefined) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (vehicleId: string) => deleteVehicleApi(applicationId!, vehicleId),
    onSuccess: () => {
      if (!applicationId) return
      void queryClient.invalidateQueries({
        queryKey: queryKeys.applicant.applicationEditModel(applicationId),
      })
    },
  })
}

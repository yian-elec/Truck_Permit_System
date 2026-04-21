import { SectionCard } from '@/shared/ui'

import { useApplicationEditModel } from '@/features/application/hooks/useApplicationEditModel'

import { useDeleteVehicle } from '../hooks/useDeleteVehicle'
import { VehicleCard } from './VehicleCard'
import { VehicleFormDialog } from './VehicleFormDialog'

export function VehicleList({ applicationId }: { applicationId: string }) {
  const edit = useApplicationEditModel(applicationId)
  const del = useDeleteVehicle(applicationId)

  const vehicles = edit.data?.detail?.vehicles ?? []

  return (
    <SectionCard title="車輛">
      <div className="mb-4 flex justify-end">
        <VehicleFormDialog applicationId={applicationId} />
      </div>
      <div className="space-y-2">
        {vehicles.length === 0 ? (
          <p className="text-sm text-muted-foreground">尚無車輛資料。</p>
        ) : (
          vehicles.map((v) => (
            <VehicleCard
              key={v.vehicle_id}
              plateNo={v.plate_no}
              kind={v.vehicle_kind}
              weight={v.gross_weight_ton ?? undefined}
              onDelete={() =>
                del.mutate(v.vehicle_id, {
                  onError: () => {},
                })
              }
            />
          ))
        )}
      </div>
    </SectionCard>
  )
}

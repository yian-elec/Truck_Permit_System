import { z } from 'zod'

import { VEHICLE_KIND_VALUES } from '@/shared/constants/application-options'

export const routeRequestFormSchema = z.object({
  origin_text: z.string().min(1),
  destination_text: z.string().min(1),
  requested_departure_at: z.string().min(1),
  vehicle_weight_ton: z.coerce.number().positive(),
  vehicle_kind: z.enum(VEHICLE_KIND_VALUES),
})

export type RouteRequestFormValues = z.infer<typeof routeRequestFormSchema>

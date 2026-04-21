import { z } from 'zod'

import { VEHICLE_KIND_VALUES } from '@/shared/constants/application-options'
import {
  normalizeVehiclePlateInput,
  VEHICLE_PLATE_NORMALIZED_REGEX,
} from '@/shared/lib/normalize-vehicle-plate'

const plateMessage =
  '車牌須為 2～20 個英數字或連字號（已自動去除空格、統一橫線格式）'

export const vehicleFormSchema = z.object({
  plate_no: z
    .string()
    .transform((s) => normalizeVehiclePlateInput(s))
    .pipe(
      z.string().regex(VEHICLE_PLATE_NORMALIZED_REGEX, {
        message: plateMessage,
      }),
    ),
  vehicle_kind: z.enum(VEHICLE_KIND_VALUES),
  gross_weight_ton: z.coerce.number().positive(),
  /** 後端為可選 date；若填請用 YYYY-MM-DD（或由 API 載入之 ISO 會在送出前截成日期） */
  license_valid_until: z
    .string()
    .optional()
    .transform((s) => {
      const t = (s ?? '').trim()
      if (!t) return ''
      return t.includes('T') ? t.slice(0, 10) : t
    }),
  trailer_plate_no: z
    .string()
    .optional()
    .transform((s) => normalizeVehiclePlateInput(s ?? ''))
    .refine((s) => s === '' || VEHICLE_PLATE_NORMALIZED_REGEX.test(s), {
      message: plateMessage,
    }),
})

export type VehicleFormValues = z.infer<typeof vehicleFormSchema>

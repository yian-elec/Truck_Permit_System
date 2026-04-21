import { z } from 'zod'

export const emailSchema = z.string().trim().email('Invalid email')

export const requiredStringSchema = z.string().trim().min(1, 'Required')

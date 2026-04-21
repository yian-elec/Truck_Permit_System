import { describe, expect, it } from 'vitest'
import { z } from 'zod'

import { parseApiData } from './response-parser'

describe('parseApiData', () => {
  it('unwraps data envelope', () => {
    const schema = z.object({ id: z.string() })
    const result = parseApiData(schema, { data: { id: 'x' } })
    expect(result).toEqual({ id: 'x' })
  })
})

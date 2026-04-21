import { describe, expect, it } from 'vitest'

import { isApiEnvelope } from './envelope'

describe('isApiEnvelope', () => {
  it('returns true for envelope-shaped objects', () => {
    expect(isApiEnvelope({ data: { a: 1 }, error: null })).toBe(true)
  })

  it('returns false for plain objects', () => {
    expect(isApiEnvelope({ foo: 1 })).toBe(false)
  })
})

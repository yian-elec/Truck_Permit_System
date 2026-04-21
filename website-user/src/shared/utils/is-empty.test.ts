import { describe, expect, it } from 'vitest'

import { isEmpty } from './is-empty'

describe('isEmpty', () => {
  it('returns true for nullish and blank strings', () => {
    expect(isEmpty(null)).toBe(true)
    expect(isEmpty(undefined)).toBe(true)
    expect(isEmpty('')).toBe(true)
    expect(isEmpty('  ')).toBe(true)
  })

  it('returns true for empty collections', () => {
    expect(isEmpty([])).toBe(true)
    expect(isEmpty({})).toBe(true)
  })

  it('returns false for meaningful values', () => {
    expect(isEmpty('a')).toBe(false)
    expect(isEmpty([1])).toBe(false)
    expect(isEmpty({ a: 1 })).toBe(false)
    expect(isEmpty(0)).toBe(false)
  })
})

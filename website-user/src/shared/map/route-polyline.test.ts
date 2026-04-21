import { describe, expect, it } from 'vitest'

import { pathsFromRoutePreview } from './route-polyline'

describe('pathsFromRoutePreview', () => {
  it('parses coordinate arrays', () => {
    const path = pathsFromRoutePreview({
      polyline: [{ lat: 1, lng: 2 }],
    })
    expect(path).toEqual([{ lat: 1, lng: 2 }])
  })

  it('returns empty for invalid', () => {
    expect(pathsFromRoutePreview(null)).toEqual([])
  })
})

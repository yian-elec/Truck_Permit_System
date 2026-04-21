import { describe, expect, it } from 'vitest'

import { formatFileSize } from './format-file-size'

describe('formatFileSize', () => {
  it('formats bytes', () => {
    expect(formatFileSize(0)).toBe('0 B')
    expect(formatFileSize(512)).toContain('B')
    expect(formatFileSize(2048)).toContain('KB')
  })
})

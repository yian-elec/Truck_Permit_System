import { describe, expect, it } from 'vitest'
import axios from 'axios'

import { ApiError, getErrorMessage } from './api-error'

describe('ApiError.fromUnknown', () => {
  it('reads backend { error: { code, message } } envelope', () => {
    const err = new axios.AxiosError('Request failed')
    err.response = {
      status: 409,
      data: {
        data: null,
        error: { code: 'ConflictError', message: 'Email already registered' },
      },
    } as typeof err.response

    const a = ApiError.fromUnknown(err)
    expect(a.message).toBe('Email already registered')
    expect(a.code).toBe('ConflictError')
  })
})

describe('getErrorMessage', () => {
  it('returns message from wrapped error', () => {
    expect(getErrorMessage(new ApiError({ message: 'oops' }))).toBe('oops')
  })
})

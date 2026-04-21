import { describe, expect, it } from 'vitest'

import { buildPatchApplicationBody } from './build-patch-application-body'
import { defaultApplicantProfileFormValues, defaultCompanyProfileFormValues } from '../validators/profile-form.schema'

describe('buildPatchApplicationBody', () => {
  it('includes object_key-aligned patch fields and applicant profile when name set', () => {
    const body = buildPatchApplicationBody(
      {
        reason_type: 'construction',
        reason_detail: '',
        requested_start_at: '2026-06-01T00:00:00.000Z',
        requested_end_at: '',
        delivery_method: 'mail',
      },
      { ...defaultApplicantProfileFormValues(), name: 'Jane Doe', email: 'j@ex.com' },
      defaultCompanyProfileFormValues(),
    )

    expect(body.patch?.reason_type).toBe('construction')
    expect(body.patch?.delivery_method).toBe('mail')
    expect(body.patch?.requested_start_at).toBe('2026-06-01T00:00:00.000Z')
    expect(body.patch?.requested_end_at).toBeUndefined()
    expect(body.profiles?.applicant?.name).toBe('Jane Doe')
    expect(body.profiles?.applicant?.email).toBe('j@ex.com')
  })

  it('includes company profile when any company field is non-empty', () => {
    const body = buildPatchApplicationBody(
      {
        reason_type: '',
        reason_detail: '',
        requested_start_at: '',
        requested_end_at: '',
        delivery_method: '',
      },
      defaultApplicantProfileFormValues(),
      { ...defaultCompanyProfileFormValues(), company_name: 'ACME' },
    )

    expect(body.patch).toBeUndefined()
    expect(body.profiles?.company?.company_name).toBe('ACME')
  })
})

import { useApplicantHomePageModel } from '@/features/page-model/hooks/useApplicantHomePageModel'

/** Alias: applicant-home uses same page model query as `page-model`. */
export function useApplicantHomeModel() {
  return useApplicantHomePageModel()
}

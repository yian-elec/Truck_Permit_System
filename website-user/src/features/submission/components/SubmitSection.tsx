import { toast } from 'sonner'

import { getErrorMessage } from '@/shared/api/api-error'
import { Button, SectionCard } from '@/shared/ui'

import { useSubmitApplication } from '../hooks/useSubmitApplication'

export function SubmitSection({ applicationId }: { applicationId: string }) {
  const submit = useSubmitApplication(applicationId)

  return (
    <SectionCard title="送出申請">
      <Button
        type="button"
        loading={submit.isPending}
        onClick={() =>
          submit.mutate(undefined, {
            onSuccess: () => {
              toast.success('已送出')
            },
            onError: (e) => toast.error(getErrorMessage(e)),
          })
        }
      >
        送出申請
      </Button>
    </SectionCard>
  )
}

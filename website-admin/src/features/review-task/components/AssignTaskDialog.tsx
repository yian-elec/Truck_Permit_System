import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { FormProvider, useForm } from 'react-hook-form'
import { toast } from 'sonner'
import { z } from 'zod'

import { queryKeys } from '@/shared/constants/query-keys'
import { ApiError } from '@/shared/api/api-error'
import {
  Button,
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  Form,
  FormField,
  Input,
} from '@/shared/ui'

import { assignReviewTask } from '../api/review-task-api'

const schema = z.object({
  assignee_user_id: z.string().uuid({ message: '請輸入有效 UUID' }),
})

type FormValues = z.infer<typeof schema>

type Props = {
  open: boolean
  onOpenChange: (open: boolean) => void
  applicationId: string | null
}

export function AssignTaskDialog({ open, onOpenChange, applicationId }: Props) {
  const queryClient = useQueryClient()
  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { assignee_user_id: '' },
  })

  const mutation = useMutation({
    mutationFn: (assignee_user_id: string) => {
      if (!applicationId) throw new Error('missing application')
      return assignReviewTask(applicationId, assignee_user_id)
    },
    onSuccess: async () => {
      toast.success('已指派承辦')
      onOpenChange(false)
      form.reset()
      await queryClient.invalidateQueries({ queryKey: queryKeys.review.tasks })
    },
    onError: (e) => {
      toast.error(ApiError.fromUnknown(e).message)
    },
  })

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>指派承辦</DialogTitle>
          <DialogDescription>輸入承辦人員之使用者 UUID。</DialogDescription>
        </DialogHeader>
        <FormProvider {...form}>
          <Form
            onSubmit={form.handleSubmit((values) => mutation.mutate(values.assignee_user_id))}
            className="space-y-4"
          >
            <FormField<FormValues>
              name="assignee_user_id"
              label="assignee_user_id"
              children={(field) => (
                <Input
                  id="assignee_user_id"
                  name={field.name}
                  ref={field.ref as React.Ref<HTMLInputElement>}
                  value={String(field.value ?? '')}
                  onBlur={field.onBlur}
                  onChange={field.onChange}
                  placeholder="00000000-0000-4000-8000-000000000000"
                />
              )}
            />
            <Button type="submit" className="w-full" loading={mutation.isPending}>
              確認指派
            </Button>
          </Form>
        </FormProvider>
      </DialogContent>
    </Dialog>
  )
}

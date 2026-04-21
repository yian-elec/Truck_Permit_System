import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { FormProvider, useForm } from 'react-hook-form'
import { toast } from 'sonner'
import { z } from 'zod'

import { queryKeys } from '@/shared/constants/query-keys'
import { ApiError } from '@/shared/api/api-error'
import { Button, Form, FormField, Input } from '@/shared/ui'

import { postComment } from '../api/review-comment-api'

const schema = z.object({
  comment_type: z.string().min(1, '必填'),
  content: z.string().min(1, '必填'),
})

type FormValues = z.infer<typeof schema>

export function CommentForm({ applicationId }: { applicationId: string }) {
  const queryClient = useQueryClient()
  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { comment_type: 'internal', content: '' },
  })

  const mutation = useMutation({
    mutationFn: (values: FormValues) => postComment(applicationId, values),
    onSuccess: async () => {
      toast.success('已送出評論')
      form.reset({ comment_type: 'internal', content: '' })
      await queryClient.invalidateQueries({ queryKey: queryKeys.review.caseDetail(applicationId) })
    },
    onError: (e) => toast.error(ApiError.fromUnknown(e).message),
  })

  return (
    <FormProvider {...form}>
      <Form onSubmit={form.handleSubmit((v) => mutation.mutate(v))} className="space-y-3">
        <FormField<FormValues>
          name="comment_type"
          label="類型"
          children={(field) => (
            <Input
              name={field.name}
              ref={field.ref as React.Ref<HTMLInputElement>}
              value={String(field.value ?? '')}
              onBlur={field.onBlur}
              onChange={field.onChange}
              placeholder="internal / supplement / decision_note"
            />
          )}
        />
        <FormField<FormValues>
          name="content"
          label="內容"
          children={(field) => (
            <textarea
              className="border-input bg-background ring-offset-background placeholder:text-muted-foreground focus-visible:ring-ring flex min-h-[96px] w-full rounded-md border px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2"
              name={field.name}
              ref={field.ref as React.Ref<HTMLTextAreaElement>}
              value={String(field.value ?? '')}
              onBlur={field.onBlur}
              onChange={field.onChange}
            />
          )}
        />
        <Button type="submit" size="sm" loading={mutation.isPending}>
          送出評論
        </Button>
      </Form>
    </FormProvider>
  )
}

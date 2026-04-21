import { useMutation } from '@tanstack/react-query'

import { createUploadUrlApi } from '../api/create-upload-url'

export function useCreateUploadUrl(applicationId: string | undefined) {
  return useMutation({
    mutationFn: (body: { mime_type: string }) => createUploadUrlApi(applicationId!, body),
  })
}

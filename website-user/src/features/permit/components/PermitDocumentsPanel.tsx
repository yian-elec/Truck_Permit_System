import { toast } from 'sonner'

import { ApiError } from '@/shared/api/api-error'
import { Button, SectionCard } from '@/shared/ui'

import { usePermitDownload } from '../hooks/usePermitDownload'

export function PermitDocumentsPanel({ applicationId }: { applicationId: string }) {
  const download = usePermitDownload(applicationId)

  return (
    <SectionCard title="文件下載">
      <p className="text-muted-foreground mb-3 text-sm">
        若尚未產製完成，按下後會於此連線內完成產檔再下載（按鈕會顯示處理中）；已產製過則直接取得檔案。
      </p>
      <Button
        type="button"
        loading={download.isPending}
        onClick={() =>
          download.mutate(undefined, {
            onError: (err) => {
              const e = ApiError.fromUnknown(err)
              toast.error(e.message || '下載失敗')
            },
          })
        }
      >
        下載通行證文件
      </Button>
    </SectionCard>
  )
}

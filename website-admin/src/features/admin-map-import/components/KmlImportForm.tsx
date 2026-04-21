import { useState } from 'react'

import { Button, Input } from '@/shared/ui'

const DEFAULT_KML_SOURCE_URL =
  'https://www.google.com/maps/d/kml?mid=1_Ozq3ZEEOut26RnltJzkSqsFG858gQY'

function initialKmlSourceDescription(): string {
  const fromEnv = import.meta.env.VITE_DEFAULT_KML_URL?.trim()
  return fromEnv || DEFAULT_KML_SOURCE_URL
}

export function KmlImportForm({
  onSubmit,
  loading,
}: {
  onSubmit: (sourceDescription: string) => void
  loading?: boolean
}) {
  const [desc, setDesc] = useState(initialKmlSourceDescription)
  return (
    <div className="space-y-2">
      <p className="text-muted-foreground text-sm">
        請貼上 <strong className="font-medium text-foreground">HTTP(S) 的 .kml / .kmz 網址</strong>
        （例如 Google「我的地圖」匯出連結），或貼上完整 <strong className="font-medium text-foreground">KML XML</strong>
        內容。匯入成功後須至圖資 Layer 發布，審查端自動規劃才會使用新規則。
      </p>
      <div className="flex flex-wrap items-end gap-2">
        <div className="min-w-[16rem] flex-1">
          <label className="text-muted-foreground mb-1 block text-xs font-medium">來源（URL 或 inline KML）</label>
          <Input
            value={desc}
            onChange={(e) => setDesc(e.target.value)}
            placeholder="https://…/data.kml 或 <?xml …><kml>…"
          />
        </div>
        <Button type="button" loading={loading} onClick={() => onSubmit(desc)}>
          送出匯入
        </Button>
      </div>
    </div>
  )
}

import { Input } from '@/shared/ui'

type Props = {
  keyword: string
  onKeywordChange: (v: string) => void
  status: string
  onStatusChange: (v: string) => void
  stage: string
  onStageChange: (v: string) => void
}

export function ReviewTaskFilters({
  keyword,
  onKeywordChange,
  status,
  onStatusChange,
  stage,
  onStageChange,
}: Props) {
  return (
    <div className="flex flex-wrap gap-3">
      <div className="min-w-[12rem] flex-1">
        <label className="text-muted-foreground mb-1 block text-xs font-medium">關鍵字</label>
        <Input
          value={keyword}
          onChange={(e) => onKeywordChange(e.target.value)}
          placeholder="任務 ID / 案件 ID"
        />
      </div>
      <div className="w-40">
        <label className="text-muted-foreground mb-1 block text-xs font-medium">狀態</label>
        <Input value={status} onChange={(e) => onStatusChange(e.target.value)} placeholder="全部" />
      </div>
      <div className="w-40">
        <label className="text-muted-foreground mb-1 block text-xs font-medium">階段</label>
        <Input value={stage} onChange={(e) => onStageChange(e.target.value)} placeholder="全部" />
      </div>
    </div>
  )
}

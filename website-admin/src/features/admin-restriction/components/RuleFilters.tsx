import { Input } from '@/shared/ui'

type Props = {
  layerId: string
  onLayerIdChange: (v: string) => void
  isActive: boolean | ''
  onIsActiveChange: (v: boolean | '') => void
  ruleType: string
  onRuleTypeChange: (v: string) => void
  keyword: string
  onKeywordChange: (v: string) => void
}

export function RuleFilters({
  layerId,
  onLayerIdChange,
  isActive,
  onIsActiveChange,
  ruleType,
  onRuleTypeChange,
  keyword,
  onKeywordChange,
}: Props) {
  return (
    <div className="flex flex-wrap gap-3">
      <div className="min-w-[10rem] flex-1">
        <label className="text-muted-foreground mb-1 block text-xs font-medium">layer_id（API）</label>
        <Input value={layerId} onChange={(e) => onLayerIdChange(e.target.value)} placeholder="UUID 篩選" />
      </div>
      <div className="w-36">
        <label className="text-muted-foreground mb-1 block text-xs font-medium">is_active</label>
        <select
          className="border-input bg-background h-9 w-full rounded-md border px-2 text-sm"
          value={isActive === '' ? '' : isActive ? 'true' : 'false'}
          onChange={(e) => {
            const v = e.target.value
            if (v === '') onIsActiveChange('')
            else onIsActiveChange(v === 'true')
          }}
        >
          <option value="">全部</option>
          <option value="true">啟用</option>
          <option value="false">停用</option>
        </select>
      </div>
      <div className="w-40">
        <label className="text-muted-foreground mb-1 block text-xs font-medium">rule_type（本地）</label>
        <Input value={ruleType} onChange={(e) => onRuleTypeChange(e.target.value)} />
      </div>
      <div className="min-w-[10rem] flex-1">
        <label className="text-muted-foreground mb-1 block text-xs font-medium">keyword（本地）</label>
        <Input value={keyword} onChange={(e) => onKeywordChange(e.target.value)} placeholder="名稱 / ID" />
      </div>
    </div>
  )
}

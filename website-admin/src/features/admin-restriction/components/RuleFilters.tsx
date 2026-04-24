import { useQuery } from '@tanstack/react-query'
import type { ChangeEvent } from 'react'

import { queryKeys } from '@/shared/constants/query-keys'
import { Input } from '@/shared/ui'

import { listMapLayers } from '@/features/admin-map-layer/api/map-layer-api'

import { RULE_TYPE_OPTIONS } from '../api/restriction-api'

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
  const layersQ = useQuery({
    queryKey: queryKeys.admin.mapLayers,
    queryFn: listMapLayers,
  })
  const layers = layersQ.data ?? []

  const layerOptions = [
    { value: '', label: '全部圖資版本' },
    ...layers.map((l) => ({
      value: l.layer_id,
      label: `${l.layer_name}（v${l.version_no}）`,
    })),
  ]

  const selectValue = layers.some((l) => l.layer_id === layerId) || layerId === '' ? layerId : ''

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-3">
        <div className="min-w-[12rem] flex-1">
          <label className="text-muted-foreground mb-1 block text-xs font-medium">圖資版本</label>
          <select
            aria-label="圖資版本"
            className="border-input bg-background h-9 w-full rounded-md border px-2 text-sm"
            value={selectValue}
            onChange={(e: ChangeEvent<HTMLSelectElement>) => onLayerIdChange(e.target.value)}
          >
            {layerOptions.map((o) => (
              <option key={o.value || 'all'} value={o.value}>
                {o.label}
              </option>
            ))}
          </select>
        </div>
        <div className="w-36">
          <label className="text-muted-foreground mb-1 block text-xs font-medium">啟用狀態</label>
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
        <div className="min-w-[11rem]">
          <label className="text-muted-foreground mb-1 block text-xs font-medium">規則類型</label>
          <select
            aria-label="規則類型"
            className="border-input bg-background h-9 w-full min-w-[10rem] rounded-md border px-2 text-sm"
            value={ruleType}
            onChange={(e: ChangeEvent<HTMLSelectElement>) => onRuleTypeChange(e.target.value)}
          >
            {RULE_TYPE_OPTIONS.map((o) => (
              <option key={o.value || 'all'} value={o.value}>
                {o.label}
              </option>
            ))}
          </select>
        </div>
        <div className="min-w-[10rem] flex-1">
          <label className="text-muted-foreground mb-1 block text-xs font-medium">關鍵字</label>
          <Input
            value={keyword}
            onChange={(e) => onKeywordChange(e.target.value)}
            placeholder="規則名稱或 ID"
          />
        </div>
      </div>

      <details className="rounded-md border border-border bg-muted/20 p-3 text-sm">
        <summary className="cursor-pointer font-medium text-foreground">進階：以 layer_id（UUID）篩選</summary>
        <p className="text-muted-foreground mt-2 text-xs">
          與上方「圖資版本」連動；可直接貼上後端回傳之 UUID（下拉未列出的版本亦可）。
        </p>
        <div className="mt-2 max-w-xl">
          <Input
            value={layerId}
            onChange={(e) => onLayerIdChange(e.target.value)}
            placeholder="00000000-0000-0000-0000-000000000000"
            className="font-mono text-xs"
          />
        </div>
      </details>
    </div>
  )
}

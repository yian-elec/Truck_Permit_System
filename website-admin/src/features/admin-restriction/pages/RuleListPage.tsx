import { useQuery } from '@tanstack/react-query'
import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'

import { queryKeys } from '@/shared/constants/query-keys'
import { routePaths } from '@/shared/constants/route-paths'
import { ApiError } from '@/shared/api/api-error'
import { formatDate } from '@/shared/utils/format-date'
import { Button, DataTable, type DataTableColumn, FilterBar, SectionCard, StatusBadge } from '@/shared/ui'

import type { RuleListItem } from '../api/restriction-api'
import { listRules } from '../api/restriction-api'
import { RuleFilters } from '../components/RuleFilters'

export function RuleListPage() {
  const [layerId, setLayerId] = useState('')
  const [isActive, setIsActive] = useState<boolean | ''>('')
  const [ruleType, setRuleType] = useState('')
  const [keyword, setKeyword] = useState('')

  const q = useQuery({
    queryKey: [...queryKeys.admin.rules, layerId, isActive] as const,
    queryFn: () =>
      listRules({
        layer_id: layerId || undefined,
        is_active: isActive === '' ? undefined : isActive,
      }),
  })

  const filtered = useMemo(() => {
    const rows = q.data ?? []
    return rows.filter((r) => {
      if (ruleType && !r.rule_type.toLowerCase().includes(ruleType.toLowerCase())) return false
      if (keyword) {
        const k = keyword.toLowerCase()
        if (!r.rule_name.toLowerCase().includes(k) && !r.rule_id.toLowerCase().includes(k)) return false
      }
      return true
    })
  }, [q.data, ruleType, keyword])

  const columns: DataTableColumn<RuleListItem>[] = [
    { id: 'name', header: '規則名稱', cell: (r) => r.rule_name },
    { id: 'type', header: '類型', cell: (r) => r.rule_type },
    { id: 'prio', header: '優先級', cell: (r) => String(r.priority) },
    {
      id: 'active',
      header: '啟用',
      cell: (r) => <StatusBadge status={r.is_active ? 'active' : 'inactive'} />,
    },
    { id: 'updated', header: '更新時間', cell: (r) => formatDate(r.updated_at) },
    {
      id: 'go',
      header: '',
      cell: (r) => (
        <Button asChild variant="outline" size="sm">
          <Link to={routePaths.ruleDetail(r.rule_id)}>查看 / 編輯</Link>
        </Button>
      ),
    },
  ]

  return (
    <div className="space-y-4">
      <div className="flex justify-end">
        <Button asChild>
          <Link to={routePaths.ruleDetail('new')}>新增規則</Link>
        </Button>
      </div>
      <SectionCard title="限制規則">
        <FilterBar>
          <RuleFilters
            layerId={layerId}
            onLayerIdChange={setLayerId}
            isActive={isActive}
            onIsActiveChange={setIsActive}
            ruleType={ruleType}
            onRuleTypeChange={setRuleType}
            keyword={keyword}
            onKeywordChange={setKeyword}
          />
        </FilterBar>
        <div className="mt-4">
          {q.isLoading ? (
            <p className="text-muted-foreground text-sm">載入中…</p>
          ) : q.isError ? (
            <div className="space-y-2">
              <p className="text-destructive text-sm">
                無法載入規則列表（{ApiError.fromUnknown(q.error).message}）。
              </p>
              <Button type="button" variant="outline" size="sm" onClick={() => void q.refetch()}>
                重試
              </Button>
            </div>
          ) : (
            <DataTable columns={columns} data={filtered} getRowId={(r) => r.rule_id} />
          )}
        </div>
      </SectionCard>
    </div>
  )
}

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useEffect, useMemo, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { toast } from 'sonner'

import { queryKeys } from '@/shared/constants/query-keys'
import { routePaths } from '@/shared/constants/route-paths'
import { ApiError } from '@/shared/api/api-error'
import { Button, SectionCard, StatusBadge } from '@/shared/ui'

import {
  activateRule,
  createRule,
  deactivateRule,
  getRule,
  patchRule,
  type RuleDetail,
} from '../api/restriction-api'
import { RuleForm } from '../components/RuleForm'

export function RuleDetailPage() {
  const { ruleId = '' } = useParams<{ ruleId: string }>()
  const isNew = ruleId === 'new'
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [form, setForm] = useState<Record<string, string>>({})

  useEffect(() => {
    setForm({})
  }, [ruleId])

  const detailQuery = useQuery({
    queryKey: queryKeys.admin.ruleDetail(ruleId),
    queryFn: () => getRule(ruleId),
    enabled: Boolean(ruleId) && !isNew,
  })

  const merged = useMemo(() => {
    if (isNew) return { ...form }
    const d = detailQuery.data
    if (!d) return { ...form }
    const base = {
      rule_id: d.rule_id,
      layer_id: d.layer_id,
      rule_name: d.rule_name,
      rule_type: d.rule_type,
      weight_limit_ton: d.weight_limit_ton != null ? String(d.weight_limit_ton) : '',
      priority: String(d.priority),
      time_rule_text: d.time_rule_text ?? '',
      effective_from: d.effective_from ?? '',
      effective_to: d.effective_to ?? '',
      is_active: d.is_active,
    }
    return { ...base, ...form }
  }, [isNew, detailQuery.data, form])

  const saveMut = useMutation({
    mutationFn: async () => {
      if (isNew) {
        return createRule({
          layer_id: merged.layer_id,
          rule_name: merged.rule_name,
          rule_type: merged.rule_type,
          weight_limit_ton: merged.weight_limit_ton ? Number(merged.weight_limit_ton) : null,
          priority: merged.priority ? Number(merged.priority) : 100,
          time_rule_text: merged.time_rule_text || null,
          effective_from: merged.effective_from || null,
          effective_to: merged.effective_to || null,
        })
      }
      return patchRule(ruleId, {
        rule_name: merged.rule_name,
        weight_limit_ton: merged.weight_limit_ton ? Number(merged.weight_limit_ton) : null,
        priority: merged.priority ? Number(merged.priority) : undefined,
        time_rule_text: merged.time_rule_text || null,
        effective_from: merged.effective_from || null,
        effective_to: merged.effective_to || null,
      })
    },
    onSuccess: (data: RuleDetail) => {
      toast.success('已儲存')
      void queryClient.invalidateQueries({ queryKey: queryKeys.admin.rules })
      if (isNew && data.rule_id) {
        queryClient.setQueryData(queryKeys.admin.ruleDetail(data.rule_id), data)
        navigate(routePaths.ruleDetail(data.rule_id), { replace: true })
      } else {
        queryClient.setQueryData(queryKeys.admin.ruleDetail(ruleId), data)
        void queryClient.invalidateQueries({ queryKey: queryKeys.admin.ruleDetail(ruleId) })
      }
    },
    onError: (e) => toast.error(ApiError.fromUnknown(e).message),
  })

  const activateMut = useMutation({
    mutationFn: () => activateRule(ruleId),
    onSuccess: async (data: RuleDetail) => {
      toast.success('已啟用')
      queryClient.setQueryData(queryKeys.admin.ruleDetail(ruleId), data)
      await queryClient.invalidateQueries({ queryKey: queryKeys.admin.ruleDetail(ruleId) })
      await queryClient.invalidateQueries({ queryKey: queryKeys.admin.rules })
    },
    onError: (e) => toast.error(ApiError.fromUnknown(e).message),
  })

  const deactivateMut = useMutation({
    mutationFn: () => deactivateRule(ruleId),
    onSuccess: async (data: RuleDetail) => {
      toast.success('已停用')
      queryClient.setQueryData(queryKeys.admin.ruleDetail(ruleId), data)
      await queryClient.invalidateQueries({ queryKey: queryKeys.admin.ruleDetail(ruleId) })
      await queryClient.invalidateQueries({ queryKey: queryKeys.admin.rules })
    },
    onError: (e) => toast.error(ApiError.fromUnknown(e).message),
  })

  function patchField(patch: Record<string, string>) {
    setForm((f) => ({ ...f, ...patch }))
  }

  if (!isNew && detailQuery.isLoading) return <p className="text-muted-foreground text-sm">載入中…</p>
  if (!isNew && detailQuery.isError) return <p className="text-destructive text-sm">無法載入規則</p>

  return (
    <div className="space-y-6">
      {!isNew && detailQuery.data ? (
        <div className="flex flex-wrap items-center gap-2">
          <StatusBadge status={detailQuery.data.is_active ? 'active' : 'inactive'} />
          <span className="text-muted-foreground font-mono text-xs">{detailQuery.data.rule_id}</span>
        </div>
      ) : null}

      <SectionCard title="規則資料" description={isNew ? '建立新規則' : '編輯規則'}>
        <RuleForm
          value={merged as Record<string, unknown>}
          onChange={patchField}
          disabled={!isNew && detailQuery.isLoading}
        />
        <div className="mt-6 flex flex-wrap gap-2">
          <Button type="button" loading={saveMut.isPending} onClick={() => saveMut.mutate()}>
            儲存
          </Button>
          {!isNew ? (
            <>
              <Button type="button" variant="secondary" loading={activateMut.isPending} onClick={() => activateMut.mutate()}>
                啟用
              </Button>
              <Button
                type="button"
                variant="outline"
                loading={deactivateMut.isPending}
                onClick={() => deactivateMut.mutate()}
              >
                停用
              </Button>
            </>
          ) : null}
        </div>
      </SectionCard>
    </div>
  )
}

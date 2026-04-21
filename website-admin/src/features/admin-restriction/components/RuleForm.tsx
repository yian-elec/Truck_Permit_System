import type { RuleDetail } from '../api/restriction-api'

type Props = {
  value: Partial<RuleDetail> & {
    layer_id?: string
    rule_name?: string
    rule_type?: string
  }
  onChange: (patch: Record<string, string>) => void
  disabled?: boolean
}

export function RuleForm({ value, onChange, disabled }: Props) {
  return (
    <div className="grid gap-4 sm:grid-cols-2">
      <label className="space-y-1 text-sm">
        <span className="text-muted-foreground">rule_name</span>
        <input
          className="border-input bg-background h-9 w-full rounded-md border px-3"
          disabled={disabled}
          value={value.rule_name ?? ''}
          onChange={(e) => onChange({ rule_name: e.target.value })}
        />
      </label>
      <label className="space-y-1 text-sm">
        <span className="text-muted-foreground">weight_limit_ton</span>
        <input
          className="border-input bg-background h-9 w-full rounded-md border px-3"
          disabled={disabled}
          value={value.weight_limit_ton != null ? String(value.weight_limit_ton) : ''}
          onChange={(e) => onChange({ weight_limit_ton: e.target.value })}
        />
      </label>
      <label className="space-y-1 text-sm">
        <span className="text-muted-foreground">priority</span>
        <input
          className="border-input bg-background h-9 w-full rounded-md border px-3"
          disabled={disabled}
          type="number"
          value={value.priority != null ? String(value.priority) : ''}
          onChange={(e) => onChange({ priority: e.target.value })}
        />
      </label>
      <label className="space-y-1 text-sm sm:col-span-2">
        <span className="text-muted-foreground">time_rule_text</span>
        <textarea
          className="border-input bg-background min-h-[72px] w-full rounded-md border px-3 py-2"
          disabled={disabled}
          value={value.time_rule_text ?? ''}
          onChange={(e) => onChange({ time_rule_text: e.target.value })}
        />
      </label>
      <label className="space-y-1 text-sm">
        <span className="text-muted-foreground">effective_from</span>
        <input
          className="border-input bg-background h-9 w-full rounded-md border px-3"
          disabled={disabled}
          type="date"
          value={value.effective_from?.slice(0, 10) ?? ''}
          onChange={(e) => onChange({ effective_from: e.target.value })}
        />
      </label>
      <label className="space-y-1 text-sm">
        <span className="text-muted-foreground">effective_to</span>
        <input
          className="border-input bg-background h-9 w-full rounded-md border px-3"
          disabled={disabled}
          type="date"
          value={value.effective_to?.slice(0, 10) ?? ''}
          onChange={(e) => onChange({ effective_to: e.target.value })}
        />
      </label>
      <label className="space-y-1 text-sm sm:col-span-2">
        <span className="text-muted-foreground">layer_id（建立必填）</span>
        <input
          className="border-input bg-background h-9 w-full rounded-md border px-3 font-mono text-xs"
          disabled={disabled || Boolean(value.rule_id)}
          value={value.layer_id ?? ''}
          onChange={(e) => onChange({ layer_id: e.target.value })}
        />
      </label>
      <label className="space-y-1 text-sm sm:col-span-2">
        <span className="text-muted-foreground">rule_type（建立必填）</span>
        <input
          className="border-input bg-background h-9 w-full rounded-md border px-3"
          disabled={disabled || Boolean(value.rule_id)}
          value={value.rule_type ?? ''}
          onChange={(e) => onChange({ rule_type: e.target.value })}
        />
      </label>
    </div>
  )
}

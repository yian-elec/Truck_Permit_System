import { SectionCard } from '@/shared/ui'

export function AttachmentRequirementList() {
  return (
    <SectionCard
      title="應備文件（參考）"
      description="實際以本案核對清單為準；各欄上傳之檔案類型須與該欄代碼一致，送件時才視為該項已備妥。"
    >
      <p className="text-sm text-muted-foreground">
        必傳：<code className="rounded bg-muted px-1">vehicle_license_copy</code>
        （行車執照影本）；選填：
        <code className="rounded bg-muted px-1">engineering_contract_or_order</code>、
        <code className="rounded bg-muted px-1">waste_site_consent</code>、
        <code className="rounded bg-muted px-1">other_power_of_attorney</code>。
      </p>
    </SectionCard>
  )
}

import { useState } from 'react'
import {
  ChevronDown,
  ChevronUp,
  MapPin,
  Phone,
  Fax,
  User,
  Building2,
  FileText,
  StickyNote,
  Send,
  Package,
  Clock,
  Link as LinkIcon,
} from 'lucide-react'

const MAP_LINK = 'https://www.traffic.ntpc.gov.tw/home.jsp?id=e081eb8c5e64ce7e' as const

interface AccordionItemProps {
  icon: React.ElementType
  title: string
  defaultOpen?: boolean
  children: React.ReactNode
}

function AccordionItem({ icon: Icon, title, defaultOpen = false, children }: AccordionItemProps) {
  const [open, setOpen] = useState(defaultOpen)
  return (
    <div className="rounded-xl border border-border bg-background shadow-sm overflow-hidden">
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className="flex w-full items-center gap-3 px-5 py-4 text-left transition-colors hover:bg-muted/40"
      >
        <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary">
          <Icon className="h-4 w-4" />
        </span>
        <span className="flex-1 text-sm font-semibold text-foreground">{title}</span>
        {open
          ? <ChevronUp className="h-4 w-4 text-muted-foreground" />
          : <ChevronDown className="h-4 w-4 text-muted-foreground" />}
      </button>
      {open && (
        <div className="border-t border-border px-5 py-4 text-sm text-muted-foreground">
          {children}
        </div>
      )}
    </div>
  )
}

export function CaseDescriptionContent() {
  return (
    <div className="space-y-3">
      {/* 承辦資訊 */}
      <AccordionItem icon={Building2} title="承辦資訊" defaultOpen>
        <div className="space-y-2">
          <div className="flex items-start gap-2">
            <Building2 className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
            <span>新北市政府警察局交通警察大隊</span>
          </div>
          <div className="flex items-start gap-2">
            <MapPin className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
            <span>新北市中和區中正路1167號</span>
          </div>
          <div className="flex items-start gap-2">
            <User className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
            <span>承辦人員：曾臆任</span>
          </div>
          <div className="flex items-start gap-2">
            <Phone className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
            <span>(02)22255999 # 4517</span>
          </div>
          <div className="flex items-start gap-2">
            <Fax className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
            <span>(02)22259997</span>
          </div>
        </div>
      </AccordionItem>

      {/* 應備文件 */}
      <AccordionItem icon={FileText} title="應備文件">
        <ol className="list-decimal space-y-1.5 pl-5">
          <li>大貨車臨時通行證申請書（民）表一。</li>
          <li>行車執照影本（拖車使用證），依行車執照應定檢日前有效（檢驗）日期內核准通行。</li>
          <li>工程合約書或訂購單。</li>
          <li>棄土場同意書暨棄土流向證明。</li>
          <li>其他（委託書）。</li>
        </ol>
      </AccordionItem>

      {/* 備註 */}
      <AccordionItem icon={StickyNote} title="備註">
        <ul className="list-disc space-y-1.5 pl-5">
          <li>每次申請時間以 6 個月為限；核准通行日期至行車執照指定檢驗日期止。（每日 7~9 時及 17~19 時為禁止通行時段）</li>
          <li>通行起訖時間未填寫者將自申請日核予 1 個月。</li>
        </ul>
      </AccordionItem>

      {/* 申請方式 */}
      <AccordionItem icon={Send} title="申請方式">
        <ul className="list-disc space-y-1.5 pl-5">
          <li>臨櫃：親自送件，審核通過後，通知通行證申請人親領。</li>
          <li>郵寄：審核通過後，通行證申請人親領或採郵寄方式（申請人須附回郵信封）。</li>
          <li>線上：申請時，上傳相關文件表單。</li>
        </ul>
      </AccordionItem>

      {/* 交付方式 */}
      <AccordionItem icon={Package} title="交付方式">
        <p>審核通過後，通行證申請人親領或採郵寄方式（申請人須附回郵信封）。</p>
      </AccordionItem>

      {/* 處理期限 */}
      <AccordionItem icon={Clock} title="處理期限">
        <p>6 天</p>
      </AccordionItem>

      {/* 備註連結 */}
      <AccordionItem icon={LinkIcon} title="相關連結">
        <a
          className="inline-flex items-center gap-1.5 text-primary underline-offset-4 hover:underline"
          href={MAP_LINK}
          target="_blank"
          rel="noreferrer"
        >
          <LinkIcon className="h-3.5 w-3.5" />
          新北市大貨車行駛路線及禁行區域圖
        </a>
      </AccordionItem>
    </div>
  )
}

import { Button, Dialog, DialogContent, DialogHeader, DialogTitle } from '@/shared/ui'

import {
  FORM_DOWNLOAD_GROUP_LABEL,
  FORM_DOWNLOAD_ITEMS,
  type FormDownloadItem,
} from '../lib/form-download-items'

type Props = {
  open: boolean
  onOpenChange: (open: boolean) => void
}

function groupBy<T>(items: T[], key: (t: T) => string) {
  const m = new Map<string, T[]>()
  for (const t of items) {
    const k = key(t)
    const a = m.get(k) ?? []
    a.push(t)
    m.set(k, a)
  }
  return m
}

export function FormDownloadDialog({ open, onOpenChange }: Props) {
  const byGroup = groupBy(FORM_DOWNLOAD_ITEMS, (i) => i.group)

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[90vh] max-w-2xl overflow-y-auto p-0">
        <DialogHeader className="border-b border-border px-6 py-4">
          <DialogTitle>書表下載</DialogTitle>
        </DialogHeader>
        <div className="space-y-8 px-6 py-4">
          {(['procedure', 'example'] as const).map((g) => {
            const list = byGroup.get(g) ?? []
            if (!list.length) return null
            return (
              <section key={g}>
                <h3 className="mb-3 text-sm font-semibold">{FORM_DOWNLOAD_GROUP_LABEL[g]}</h3>
                <ul className="space-y-2">
                  {list.map((row: FormDownloadItem) => (
                    <li
                      key={row.url}
                      className="flex flex-wrap items-center justify-between gap-2 rounded-md border border-border px-3 py-2 text-sm"
                    >
                      <div className="min-w-0 flex-1">
                        <p className="font-medium break-words">{row.displayName}</p>
                        <p className="text-xs uppercase text-muted-foreground">{row.format}</p>
                      </div>
                      <Button variant="secondary" size="sm" asChild>
                        <a href={row.url} download>
                          下載
                        </a>
                      </Button>
                    </li>
                  ))}
                </ul>
              </section>
            )
          })}
        </div>
      </DialogContent>
    </Dialog>
  )
}

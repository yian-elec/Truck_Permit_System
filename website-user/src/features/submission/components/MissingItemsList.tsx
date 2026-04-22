import { useLocation, useNavigate } from 'react-router-dom'

import { Button } from '@/shared/ui'

import { getMissingItemActionHref, missingReasonToMessage } from '../lib/missing-reason-messages'

function goToActionHref(
  fullHref: string,
  locationPathname: string,
  navigate: ReturnType<typeof useNavigate>,
) {
  const u = new URL(fullHref, window.location.origin)
  const hash = u.hash
  if (u.pathname === locationPathname && hash) {
    const elId = decodeURIComponent(hash.slice(1))
    const el = document.getElementById(elId)
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'start' })
      return
    }
  }
  void navigate({ pathname: u.pathname, search: u.search, hash: u.hash }, { preventScrollReset: true })
  if (u.hash) {
    const elId = decodeURIComponent(u.hash.slice(1))
    const tryScroll = () => {
      const el = document.getElementById(elId)
      if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
    tryScroll()
    requestAnimationFrame(tryScroll)
    window.setTimeout(tryScroll, 200)
  }
}

export function MissingItemsList({
  items,
  applicationId,
  page = 'edit',
}: {
  items: unknown[]
  applicationId?: string
  /** 目前為編輯或預覽頁，用於同頁捲動 vs 導回編輯帶錨點 */
  page?: 'edit' | 'preview'
}) {
  const location = useLocation()
  const navigate = useNavigate()

  if (!items.length) return <p className="text-sm text-muted-foreground">無缺少項目。</p>
  return (
    <ul className="space-y-2 text-sm">
      {items.map((x, i) => {
        const code = typeof x === 'string' ? x : JSON.stringify(x)
        const label = typeof x === 'string' ? missingReasonToMessage(x) : code
        const fullHref =
          applicationId && typeof x === 'string' ? getMissingItemActionHref(applicationId, x, page) : null
        return (
          <li
            key={`${code}-${i}`}
            className="flex flex-wrap items-center justify-between gap-2 rounded-md border border-border/80 bg-muted/30 px-3 py-2"
          >
            <span className="text-destructive">{label}</span>
            {fullHref ? (
              <Button
                type="button"
                variant="link"
                className="h-auto shrink-0 p-0 text-primary underline-offset-4"
                onClick={() => goToActionHref(fullHref, location.pathname, navigate)}
              >
                前往補填
              </Button>
            ) : null}
          </li>
        )
      })}
    </ul>
  )
}

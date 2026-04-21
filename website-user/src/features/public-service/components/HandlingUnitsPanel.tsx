import type { HandlingUnitsPayload } from '../types/public-service.types'

export function HandlingUnitsPanel({ data }: { data: HandlingUnitsPayload }) {
  return (
    <section className="rounded-lg border border-border bg-background p-6 shadow-sm">
      <h3 className="text-lg font-semibold">承辦單位</h3>
      <ul className="mt-4 space-y-4">
        {data.units.length === 0 ? (
          <li className="text-sm text-muted-foreground">尚無資料。</li>
        ) : (
          data.units.map((u, i) => (
            <li key={i} className="rounded-md border border-border p-3 text-sm">
              <p className="font-medium">{u.name ?? '單位'}</p>
              {u.phone ? <p className="text-muted-foreground">{u.phone}</p> : null}
              {u.address ? <p className="text-muted-foreground">{u.address}</p> : null}
            </li>
          ))
        )}
      </ul>
    </section>
  )
}

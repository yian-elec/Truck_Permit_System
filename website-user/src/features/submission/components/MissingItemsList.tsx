export function MissingItemsList({ items }: { items: unknown[] }) {
  if (!items.length) return <p className="text-sm text-muted-foreground">無缺少項目。</p>
  return (
    <ul className="list-inside list-disc text-sm text-destructive">
      {items.map((x, i) => (
        <li key={i}>{typeof x === 'string' ? x : JSON.stringify(x)}</li>
      ))}
    </ul>
  )
}

import type { ReactNode } from 'react'

import { cn } from '@/shared/lib/cn'

export type DataTableColumn<T> = {
  id: string
  header: ReactNode
  cell: (row: T) => ReactNode
  className?: string
}

type DataTableProps<T> = {
  columns: DataTableColumn<T>[]
  data: T[]
  getRowId: (row: T) => string
  emptyMessage?: string
  className?: string
}

export function DataTable<T>({
  columns,
  data,
  getRowId,
  emptyMessage = '沒有資料',
  className,
}: DataTableProps<T>) {
  return (
    <div className={cn('border-border overflow-x-auto rounded-md border', className)}>
      <table className="w-full min-w-[32rem] border-collapse text-sm">
        <thead>
          <tr className="bg-muted/40 border-b border-border">
            {columns.map((col) => (
              <th
                key={col.id}
                className={cn('text-muted-foreground px-3 py-2 text-left font-medium', col.className)}
              >
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.length === 0 ? (
            <tr>
              <td className="text-muted-foreground px-3 py-6 text-center" colSpan={columns.length}>
                {emptyMessage}
              </td>
            </tr>
          ) : (
            data.map((row) => (
              <tr key={getRowId(row)} className="border-border hover:bg-muted/30 border-b last:border-0">
                {columns.map((col) => (
                  <td key={col.id} className={cn('px-3 py-2 align-middle', col.className)}>
                    {col.cell(row)}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  )
}

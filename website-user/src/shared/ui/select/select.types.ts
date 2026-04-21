import type * as React from 'react'

export type SelectOption = {
  value: string
  label: string
}

export type SelectProps = Omit<React.SelectHTMLAttributes<HTMLSelectElement>, 'children' | 'size'> & {
  options: SelectOption[]
  /** 若設定，會插入 value 為空的最前選項（disabled，僅作提示） */
  placeholder?: string
}

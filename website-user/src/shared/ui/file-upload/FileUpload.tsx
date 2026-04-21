import { useRef } from 'react'

import { Button } from '@/shared/ui/button/Button'

import type { WithClassName } from '@/shared/types/ui'

export type FileUploadProps = WithClassName & {
  accept?: string
  disabled?: boolean
  label?: string
  onFile: (file: File) => void
}

export function FileUpload({
  className,
  accept,
  disabled,
  label = '選擇檔案',
  onFile,
}: FileUploadProps) {
  const inputRef = useRef<HTMLInputElement>(null)

  return (
    <div className={className}>
      <input
        ref={inputRef}
        type="file"
        className="hidden"
        accept={accept}
        disabled={disabled}
        onChange={(e) => {
          const file = e.target.files?.[0]
          if (file) onFile(file)
          e.target.value = ''
        }}
      />
      <Button
        type="button"
        variant="outline"
        size="sm"
        disabled={disabled}
        onClick={() => inputRef.current?.click()}
      >
        {label}
      </Button>
    </div>
  )
}

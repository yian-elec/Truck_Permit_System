import { useEffect } from 'react'

export function useConfirmLeave(when: boolean, message = '尚未儲存的變更將遺失，確定離開？') {
  useEffect(() => {
    const handler = (e: BeforeUnloadEvent) => {
      if (!when) return
      e.preventDefault()
      e.returnValue = message
    }
    window.addEventListener('beforeunload', handler)
    return () => window.removeEventListener('beforeunload', handler)
  }, [when, message])
}

import { Component, type ErrorInfo, type ReactNode } from 'react'

import { logger } from '@/shared/lib/logger'
import { Button } from '@/shared/ui'

type Props = { children: ReactNode }

type State = { error: Error | null }

export class RootErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { error: null }
  }

  static getDerivedStateFromError(error: Error): State {
    return { error }
  }

  componentDidCatch(error: Error, info: ErrorInfo): void {
    logger.error('Root error boundary', error, info.componentStack)
  }

  render(): ReactNode {
    if (this.state.error) {
      return (
        <div className="bg-background flex min-h-screen flex-col items-center justify-center gap-4 p-8 text-center">
          <h1 className="text-xl font-semibold">頁面發生未預期錯誤</h1>
          <p className="text-muted-foreground max-w-md text-sm">
            請重新載入頁面。若問題持續，請聯絡系統管理員並提供發生時間與操作步驟。
          </p>
          <Button type="button" onClick={() => window.location.reload()}>
            重新載入
          </Button>
        </div>
      )
    }
    return this.props.children
  }
}

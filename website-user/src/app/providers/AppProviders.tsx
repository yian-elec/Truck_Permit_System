import { QueryProvider } from './query-provider'
import { AppRouterProvider } from './router-provider'
import { ThemeProvider } from './theme-provider'
import { ToastProvider } from './toast-provider'

export function AppProviders() {
  return (
    <QueryProvider>
      <ThemeProvider>
        <ToastProvider />
        <AppRouterProvider />
      </ThemeProvider>
    </QueryProvider>
  )
}

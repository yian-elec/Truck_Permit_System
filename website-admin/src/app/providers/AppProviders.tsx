import { Toaster } from 'sonner'

import { QueryProvider } from './query-provider'
import { AppRouterProvider } from './router-provider'
import { ThemeProvider } from './theme-provider'

export function AppProviders() {
  return (
    <QueryProvider>
      <ThemeProvider>
        <AppRouterProvider />
        <Toaster richColors position="top-right" />
      </ThemeProvider>
    </QueryProvider>
  )
}

import { RootErrorBoundary } from '@/app/components/RootErrorBoundary'
import { AppProviders } from '@/app/providers/AppProviders'

export default function App() {
  return (
    <RootErrorBoundary>
      <AppProviders />
    </RootErrorBoundary>
  )
}

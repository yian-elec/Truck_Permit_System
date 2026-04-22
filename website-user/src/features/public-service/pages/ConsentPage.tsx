import { Navigate } from 'react-router-dom'

import { routePaths } from '@/shared/constants/route-paths'

/**
 * 舊網址 /consent 收斂；同意條款改於申請端編輯／預覽流程內顯示。
 */
export function ConsentPage() {
  return <Navigate to={routePaths.home} replace />
}

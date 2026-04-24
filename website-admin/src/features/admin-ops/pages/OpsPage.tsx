import { Navigate } from 'react-router-dom'

import { workCenterUrl } from '@/shared/constants/route-paths'

/**
 * 舊路徑 /admin/ops 已改由路由層導向作業中心；此元件保留供可能之動態 import。
 */
export function OpsPage() {
  return <Navigate to={workCenterUrl('ocr')} replace />
}

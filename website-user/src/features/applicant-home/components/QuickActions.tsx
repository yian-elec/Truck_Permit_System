import { Link } from 'react-router-dom'

import { routePaths } from '@/shared/constants/route-paths'
import { Button } from '@/shared/ui'

export function QuickActions() {
  return (
    <div className="flex flex-wrap gap-2">
      <Button asChild>
        <Link to={routePaths.applicantApplicationNew}>新增案件</Link>
      </Button>
      <Button variant="outline" asChild>
        <Link to={routePaths.applicantApplications}>查看全部案件</Link>
      </Button>
    </div>
  )
}

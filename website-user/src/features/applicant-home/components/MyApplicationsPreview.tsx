import { Link } from 'react-router-dom'

import { routePaths } from '@/shared/constants/route-paths'
import { formatApplicationStatus } from '@/shared/utils/format-application-status'
import { formatDate } from '@/shared/utils/format-date'
import { Button, EmptyState } from '@/shared/ui'

import type { ApplicationSummary } from '../api/get-my-applications'

export function MyApplicationsPreview({ applications }: { applications: ApplicationSummary[] }) {
  if (applications.length === 0) {
    return (
      <EmptyState
        title="尚無案件"
        description="建立新案件以開始申請。"
      />
    )
  }

  return (
    <ul className="divide-y divide-border rounded-md border border-border">
      {applications.slice(0, 5).map((app) => (
        <li key={app.application_id} className="flex flex-wrap items-center justify-between gap-2 p-3 text-sm">
          <div>
            <p className="font-medium">{app.application_no}</p>
            <p className="text-xs text-muted-foreground">
              {formatApplicationStatus(app.status)} · {formatDate(app.updated_at)}
            </p>
          </div>
          <Button variant="outline" size="sm" asChild>
            <Link to={routePaths.applicantApplication(app.application_id)}>查看</Link>
          </Button>
        </li>
      ))}
    </ul>
  )
}

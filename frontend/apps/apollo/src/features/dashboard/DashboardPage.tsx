import { BookOpen, ChevronDown, LayoutDashboard, Search, Sparkles, Upload } from "lucide-react";
import {
  BottomActionBar,
  MetricCard,
  PageHeader,
  PageShell,
  SectionHeading,
  StatusPill,
  SurfacePanel,
  brand,
} from "@optimark/calliope";

import { activityFeed, assignmentRows } from "./mock-data";

export function DashboardPage() {
  return (
    <PageShell>
      <PageHeader
        title={brand.courseLabel}
        subtitle={`${brand.courseTerm} • ${brand.viewLabel}`}
        actions={
          <>
            <button className="app-secondary-action" type="button">
              <LayoutDashboard size={16} />
              Open Gradebook
            </button>
            <button className="app-primary-action" type="button">
              <Upload size={16} />
              Publish All
            </button>
          </>
        }
      />

      <div className="app-metric-grid">
        <MetricCard label="Drafts" value="4" context="Items" />
        <MetricCard label="Published" value="12" context="Live" tone="primary" />
        <MetricCard label="Pending Review" value="8" context="Grading" tone="danger" />
        <MetricCard label="Completed" value="45" context="Students" />
      </div>

      <div className="app-dashboard-grid">
        <SurfacePanel className="app-table-panel">
          <SectionHeading
            icon={<BookOpen size={16} />}
            title="Active Coursework"
            actions={
              <button className="app-inline-control" type="button">
                Filter
                <ChevronDown size={14} />
              </button>
            }
          />

          <table className="app-dense-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Type</th>
                <th>Status</th>
                <th>Due Date</th>
                <th className="align-right">Submissions</th>
              </tr>
            </thead>
            <tbody>
              {assignmentRows.map((row) => (
                <tr key={row.name}>
                  <td className="app-table-strong">{row.name}</td>
                  <td>{row.type}</td>
                  <td>
                    <StatusPill tone={row.status.tone}>{row.status.label}</StatusPill>
                  </td>
                  <td>{row.due}</td>
                  <td className="align-right app-table-strong">{row.submissions}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </SurfacePanel>

        <SurfacePanel className="app-feed-panel">
          <SectionHeading icon={<Sparkles size={16} />} title="Operational Feed" />
          <div className="app-feed-list">
            {activityFeed.map((item) => (
              <article key={item.title} className="app-feed-item">
                <div className={`app-feed-icon app-feed-icon-${item.tone}`}>{item.icon}</div>
                <div>
                  <strong>{item.title}</strong>
                  <p>{item.when}</p>
                  <span>{item.detail}</span>
                </div>
              </article>
            ))}
          </div>
        </SurfacePanel>
      </div>

      <BottomActionBar
        leading={
          <>
            <span className="app-smallcaps">Quick Actions</span>
            <button className="app-icon-button" type="button" aria-label="Search quick actions">
              <Search size={16} />
            </button>
          </>
        }
        actions={
          <>
            <button className="app-inline-action" type="button">Regrade</button>
            <button className="app-inline-action" type="button">Download CSV</button>
          </>
        }
      />
    </PageShell>
  );
}

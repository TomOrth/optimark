import { ChevronDown, Download, Filter, Settings } from "lucide-react";
import {
  BottomActionBar,
  FormFieldScaffold,
  PageShell,
  SectionHeading,
  StatusPill,
  SurfacePanel,
  brand,
} from "@optimark/calliope";

import { gradebookRows, gradeDistribution } from "./mock-data";

export function GradebookPage() {
  return (
    <PageShell>
      <div className="app-gradebook-shell">
        <div className="app-gradebook-main">
          <SurfacePanel muted className="app-overview-card">
            <h3>Academic Overview</h3>
            <p>{brand.courseLabel} • {brand.courseTerm}</p>
            <div className="app-overview-metrics">
              <div>
                <span className="app-smallcaps">Average Grade</span>
                <strong>84.2</strong>
              </div>
              <div>
                <span className="app-smallcaps">Completion Rate</span>
                <strong>92%</strong>
              </div>
              <div>
                <span className="app-smallcaps">Next Deadline</span>
                <strong>Oct 12</strong>
              </div>
            </div>
          </SurfacePanel>

          <div className="app-filter-row">
            <FormFieldScaffold label="Filter by Student">
              <div className="app-filter-pill">
                All Students
                <ChevronDown size={16} />
              </div>
            </FormFieldScaffold>
            <FormFieldScaffold label="Assignment Status">
              <div className="app-filter-pill">
                All Statuses
                <Filter size={16} />
              </div>
            </FormFieldScaffold>
            <div className="app-filter-actions">
              <button className="app-secondary-action" type="button">
                <Download size={16} />
                Export CSV
              </button>
              <button className="app-secondary-action" type="button">
                <Settings size={16} />
                View Settings
              </button>
            </div>
          </div>

          <SurfacePanel className="app-gradebook-table-panel">
            <table className="app-gradebook-table">
              <thead>
                <tr>
                  <th>Student Name</th>
                  <th>HW 1</th>
                  <th>HW 2</th>
                  <th>HW 3</th>
                  <th>HW 4</th>
                  <th>Midterm</th>
                  <th className="align-right">Overall</th>
                </tr>
              </thead>
              <tbody>
                {gradebookRows.map((row) => (
                  <tr key={row.email}>
                    <td>
                      <div className="app-student-cell">
                        <div className={`app-student-avatar app-student-avatar-${row.accent}`}>
                          {row.initials}
                        </div>
                        <div>
                          <strong>{row.student}</strong>
                          <p>{row.email}</p>
                        </div>
                      </div>
                    </td>
                    {row.scores.map((score, index) => (
                      <td key={`${row.email}-${index}`}>
                        <strong className="app-grade-cell">{score.value}</strong>
                        <StatusPill tone={score.tone}>{score.status}</StatusPill>
                      </td>
                    ))}
                    <td className={`align-right app-overall-${row.overallTone}`}>
                      {row.overall}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </SurfacePanel>
        </div>

        <SurfacePanel className="app-chart-panel">
          <SectionHeading title="Grading Distribution" />
          <div className="app-chart-bars">
            {gradeDistribution.map((bar) => (
              <div key={bar.label} className="app-chart-column">
                <div
                  className={`app-chart-bar ${bar.accent ? "app-chart-bar-accent" : ""}`}
                  style={{ height: bar.height }}
                />
                <span>{bar.label}</span>
              </div>
            ))}
          </div>
        </SurfacePanel>
      </div>

      <BottomActionBar
        leading={
          <div className="app-status-cluster">
            <span className="app-smallcaps">3 students selected</span>
            <strong>Batch actions ready</strong>
          </div>
        }
        actions={
          <>
            <button className="app-inline-action" type="button">Message</button>
            <button className="app-inline-action" type="button">Batch Edit</button>
            <button className="app-primary-action" type="button">Release Selected</button>
          </>
        }
      />
    </PageShell>
  );
}

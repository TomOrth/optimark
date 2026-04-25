import React from "react";
import ReactDOM from "react-dom/client";
import {
  QueryClient,
  QueryClientProvider,
} from "@tanstack/react-query";
import {
  RouterProvider,
  createRootRouteWithContext,
  createRoute,
  createRouter,
  redirect,
  Outlet,
  Link,
} from "@tanstack/react-router";
import {
  Bell,
  BookOpen,
  ChartColumn,
  ChevronDown,
  CircleAlert,
  Code2,
  Download,
  FileCode2,
  Filter,
  FolderOpen,
  Gauge,
  GraduationCap,
  History,
  LayoutDashboard,
  ListChecks,
  Search,
  Settings,
  Sparkles,
  SquareTerminal,
  Upload,
  Users,
} from "lucide-react";
import {
  AppFrame,
  BottomActionBar,
  BrandLockup,
  EmptyState,
  FormFieldScaffold,
  MetricCard,
  PageHeader,
  PageShell,
  SectionHeading,
  SidebarNavItem,
  SidebarShell,
  StatusPill,
  SurfacePanel,
  Topbar,
  TopbarTab,
  brand,
  sidebarUtilityLinks,
  topTabs,
} from "@optimark/calliope";
import "@optimark/calliope/system.css";
import "./styles.css";

type AppContext = {
  queryClient: QueryClient;
};

const queryClient = new QueryClient();

const navItems = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/assignments", label: "Assignments", icon: BookOpen },
  { to: "/submissions", label: "Submissions", icon: ListChecks },
  { to: "/gradebook", label: "Gradebook", icon: ChartColumn },
  { to: "/students", label: "Students", icon: Users },
  { to: "/settings", label: "Settings", icon: Settings },
] as const;

const assignmentRows = [
  {
    name: "Homework 4: Linked Lists",
    type: "Practical",
    status: { label: "Published", tone: "primary" as const },
    due: "Oct 12, 23:59",
    submissions: "42 / 45",
  },
  {
    name: "Assignment 3: Binary Trees",
    type: "Programming",
    status: { label: "Reviewing", tone: "secondary" as const },
    due: "Oct 05, 12:00",
    submissions: "45 / 45",
  },
  {
    name: "Midterm Quiz: Core Concepts",
    type: "Exam",
    status: { label: "Draft", tone: "default" as const },
    due: "Oct 24, 09:00",
    submissions: "0 / 45",
  },
  {
    name: "Homework 5: Graph Theory",
    type: "Practical",
    status: { label: "Draft", tone: "default" as const },
    due: "Nov 02, 23:59",
    submissions: "0 / 45",
  },
] as const;

const activityFeed = [
  {
    title: "Student A submitted Homework 4",
    when: "12 minutes ago",
    detail: "New programming artifact is ready for queueing.",
    tone: "primary" as const,
  },
  {
    title: "Autograde completed for Assignment 3",
    when: "45 minutes ago",
    detail: "82% average • 4 error flags surfaced for review.",
    tone: "secondary" as const,
  },
  {
    title: "Manual review started on Midterm Essays",
    when: "2 hours ago",
    detail: "TA review batch is currently in progress.",
    tone: "default" as const,
  },
  {
    title: "System: Plagiarism detected in Homework 4",
    when: "3 hours ago",
    detail: "One critical alert needs instructor verification.",
    tone: "danger" as const,
  },
] as const;

const starterFiles = [
  {
    name: "linked_list.py",
    meta: "Python Source • 2.4 KB",
    icon: <FileCode2 size={18} />,
  },
  {
    name: "test_suite.py",
    meta: "Python Test • 5.1 KB",
    icon: <SquareTerminal size={18} />,
  },
] as const;

const gradebookRows = [
  {
    initials: "AA",
    student: "Alex Abramov",
    email: "a.abramov@university.edu",
    accent: "secondary" as const,
    scores: [
      { value: "95/100", status: "Released", tone: "primary" as const },
      { value: "88/100", status: "Released", tone: "primary" as const },
      { value: "--/100", status: "Pending", tone: "secondary" as const },
      { value: "--/100", status: "Missing", tone: "default" as const },
      { value: "142/150", status: "Released", tone: "primary" as const },
    ],
    overall: "91.4%",
    overallTone: "primary" as const,
  },
  {
    initials: "EL",
    student: "Elena Laveau",
    email: "e.laveau@university.edu",
    accent: "secondary" as const,
    scores: [
      { value: "100/100", status: "Released", tone: "primary" as const },
      { value: "94/100", status: "Released", tone: "primary" as const },
      { value: "98/100", status: "Released", tone: "primary" as const },
      { value: "92/100", status: "Released", tone: "primary" as const },
      { value: "148/150", status: "Released", tone: "primary" as const },
    ],
    overall: "97.8%",
    overallTone: "primary" as const,
  },
  {
    initials: "JM",
    student: "Jordan Miller",
    email: "j.miller@university.edu",
    accent: "danger" as const,
    scores: [
      { value: "64/100", status: "Released", tone: "primary" as const },
      { value: "72/100", status: "Released", tone: "primary" as const },
      { value: "--/100", status: "Pending", tone: "secondary" as const },
      { value: "--/100", status: "Pending", tone: "secondary" as const },
      { value: "110/150", status: "Released", tone: "primary" as const },
    ],
    overall: "68.2%",
    overallTone: "danger" as const,
  },
  {
    initials: "SW",
    student: "Sarah Wu",
    email: "s.wu@university.edu",
    accent: "secondary" as const,
    scores: [
      { value: "92/100", status: "Released", tone: "primary" as const },
      { value: "89/100", status: "Released", tone: "primary" as const },
      { value: "91/100", status: "Released", tone: "primary" as const },
      { value: "88/100", status: "Released", tone: "primary" as const },
      { value: "138/150", status: "Released", tone: "primary" as const },
    ],
    overall: "90.5%",
    overallTone: "primary" as const,
  },
] as const;

const gradeDistribution = [
  { label: "F", height: "18%", accent: false },
  { label: "D", height: "42%", accent: false },
  { label: "C", height: "78%", accent: true },
  { label: "B", height: "60%", accent: false },
  { label: "A", height: "14%", accent: false },
] as const;

const rootRoute = createRootRouteWithContext<AppContext>()({
  component: RootLayout,
});

const indexRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/",
  beforeLoad: () => {
    throw redirect({ to: "/dashboard" });
  },
});

const dashboardRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/dashboard",
  component: DashboardPage,
});

const assignmentsRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/assignments",
  component: AssignmentsPage,
});

const assignmentEditorRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/assignments/new",
  component: AssignmentBuilderPage,
});

const submissionsRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/submissions",
  component: SubmissionsPage,
});

const gradebookRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/gradebook",
  component: GradebookPage,
});

const studentsRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/students",
  component: StudentsPage,
});

const settingsRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/settings",
  component: SettingsPage,
});

const routeTree = rootRoute.addChildren([
  indexRoute,
  dashboardRoute,
  assignmentsRoute,
  assignmentEditorRoute,
  submissionsRoute,
  gradebookRoute,
  studentsRoute,
  settingsRoute,
]);

const router = createRouter({
  routeTree,
  context: {
    queryClient,
  },
});

declare module "@tanstack/react-router" {
  interface Register {
    router: typeof router;
  }
}

function RootLayout() {
  return (
    <AppFrame
      sidebar={<AppSidebar />}
      topbar={<AppTopbar />}
    >
      <Outlet />
    </AppFrame>
  );
}

function AppSidebar() {
  return (
    <SidebarShell
      brand={
        <BrandLockup
          name={brand.name}
          context={brand.courseLabel}
          mark={<Code2 size={18} />}
        />
      }
      navigation={navItems.map(({ to, label, icon: Icon }) => (
        <Link key={to} to={to}>
          {({ isActive }) => (
            <SidebarNavItem
              active={isActive}
              icon={<Icon size={20} />}
              label={label}
            />
          )}
        </Link>
      ))}
      primaryAction={
        <Link to="/assignments/new" className="app-primary-action">
          New Assessment
        </Link>
      }
      utilityLinks={sidebarUtilityLinks.map((item) => (
        <div key={item.key} className="app-utility-link">
          {item.label}
        </div>
      ))}
      profile={
        <div className="app-profile-chip">
          <div className="app-profile-avatar">AT</div>
          <div>
            <strong>{brand.instructorName}</strong>
            <p>{brand.instructorRole}</p>
          </div>
        </div>
      }
    />
  );
}

function AppTopbar() {
  const path = router.state.location.pathname;
  const activeTopTab = path === "/gradebook" ? "analytics" : "course-settings";

  return (
    <Topbar
      tabs={topTabs.map((tab) => (
        <TopbarTab key={tab.key} active={tab.key === activeTopTab}>
          {tab.label}
        </TopbarTab>
      ))}
      search={
        <label className="app-search">
          <Search size={16} />
          <input placeholder="Search assessments..." />
        </label>
      }
      tools={
        <div className="app-topbar-tools">
          <button className="app-icon-button" type="button" aria-label="Notifications">
            <Bell size={18} />
          </button>
          <button className="app-icon-button" type="button" aria-label="History">
            <History size={18} />
          </button>
          <div className="app-topbar-avatar">AT</div>
        </div>
      }
    />
  );
}

function DashboardPage() {
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
          <SectionHeading
            icon={<Sparkles size={16} />}
            title="Operational Feed"
          />
          <div className="app-feed-list">
            {activityFeed.map((item) => (
              <article key={item.title} className="app-feed-item">
                <div className={`app-feed-icon app-feed-icon-${item.tone}`}>
                  {item.tone === "danger" ? <CircleAlert size={16} /> : <FileCode2 size={16} />}
                </div>
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

function AssignmentsPage() {
  return (
    <PageShell>
      <PageHeader
        eyebrow="Foundation Surface"
        title="Assignment workflows"
        subtitle="The design system now supports calm inspector layouts, file rails, and editorial form treatment for future instructor flows."
        actions={
          <Link to="/assignments/new" className="app-primary-action">
            Open Editor
          </Link>
        }
      />
      <EmptyState
        icon={<FolderOpen size={18} />}
        title="Reusable assignment patterns are ready"
        description="Issue #8 can plug actual assignment data and actions into this shared shell without restyling the workspace."
      />
    </PageShell>
  );
}

function AssignmentBuilderPage() {
  return (
    <PageShell>
      <PageHeader
        eyebrow="Assignment Editor"
        title="Homework 4: Linked Lists"
      />

      <div className="app-editor-grid">
        <div className="app-editor-main">
          <SectionHeading
            icon={<FileCode2 size={16} />}
            title="Description"
            actions={
              <div className="app-inline-group">
                <button className="app-inline-action app-inline-action-active" type="button">
                  Write
                </button>
                <button className="app-inline-action" type="button">
                  Preview
                </button>
              </div>
            }
          />

          <SurfacePanel muted className="app-editor-block">
            <pre>{`## Instructions
Implement a singly linked list with the following methods:
- append(value)
- prepend(value)
- delete(value)
- find(value)

### Constraints
- Time Complexity: O(n) for searching
- Space Complexity: O(1) for deletions

Ensure all edge cases are handled (empty list, single node list).`}</pre>
          </SurfacePanel>

          <SectionHeading
            icon={<FolderOpen size={16} />}
            title="Starter Files"
          />
          <div className="app-file-stack">
            {starterFiles.map((file) => (
              <SurfacePanel key={file.name} muted className="app-file-row">
                <div className="app-file-main">
                  <div className="app-file-icon">{file.icon}</div>
                  <div>
                    <strong>{file.name}</strong>
                    <p>{file.meta}</p>
                  </div>
                </div>
              </SurfacePanel>
            ))}
            <div className="app-upload-zone">
              <Upload size={18} />
              Upload Additional Files
            </div>
          </div>
        </div>

        <SurfacePanel muted className="app-editor-inspector">
          <SectionHeading title="Metadata" />
          <div className="app-inspector-grid">
            <FormFieldScaffold label="Due Date">
              <div className="app-field-value">Oct 15, 2026</div>
            </FormFieldScaffold>
            <FormFieldScaffold label="Points">
              <div className="app-field-value">100</div>
            </FormFieldScaffold>
            <FormFieldScaffold label="Language">
              <div className="app-field-value">Python 3.10</div>
            </FormFieldScaffold>
            <FormFieldScaffold label="Submission Limit" support="3 attempts">
              <div className="app-slider-track">
                <span />
              </div>
            </FormFieldScaffold>
          </div>
          <div className="app-inspector-meta">
            <div className="app-meta-row">
              <span>Visibility</span>
              <StatusPill>Hidden</StatusPill>
            </div>
            <div className="app-meta-row">
              <span>Category</span>
              <StatusPill tone="primary">Coding</StatusPill>
            </div>
          </div>
          <button className="app-verify-card" type="button">
            <Sparkles size={22} />
            Verify Environment
          </button>
        </SurfacePanel>
      </div>

      <BottomActionBar
        leading={
          <div className="app-status-cluster">
            <span className="app-smallcaps">Current Status</span>
            <strong>Draft Saving...</strong>
          </div>
        }
        actions={
          <>
            <button className="app-inline-action" type="button">Save Draft</button>
            <button className="app-primary-action" type="button">Publish</button>
          </>
        }
      />
    </PageShell>
  );
}

function SubmissionsPage() {
  return (
    <PageShell>
      <PageHeader
        title="Submission queue"
        subtitle="Shared list, status, and action-bar primitives are ready for student and staff queue flows."
      />
      <EmptyState
        icon={<ListChecks size={18} />}
        title="Submission workflows will plug in here"
        description="The design system now supports high-density queue views and calm operational empty states."
      />
    </PageShell>
  );
}

function GradebookPage() {
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

function StudentsPage() {
  return (
    <PageShell>
      <PageHeader
        title="Roster surfaces"
        subtitle="The shared shell, list, and metadata treatments are ready for future student-centric workflows."
      />
      <EmptyState
        icon={<GraduationCap size={18} />}
        title="Roster primitives are now part of the system"
        description="Issue-specific student views can reuse the gradebook table rhythm, metadata labels, and sidebar shell without forking styles."
      />
    </PageShell>
  );
}

function SettingsPage() {
  return (
    <PageShell>
      <PageHeader
        title="Course settings"
        subtitle="Configuration pages can reuse the same inspector and form-field scaffolds from the assignment editor."
      />
      <div className="app-settings-grid">
        <SurfacePanel muted className="app-settings-panel">
          <SectionHeading title="Grading policy" icon={<Gauge size={16} />} />
          <FormFieldScaffold label="Release cadence">
            <div className="app-field-value">Manual review gate</div>
          </FormFieldScaffold>
          <FormFieldScaffold label="Visibility default">
            <div className="app-field-value">Hidden until publish</div>
          </FormFieldScaffold>
        </SurfacePanel>
        <SurfacePanel muted className="app-settings-panel">
          <SectionHeading title="Operational defaults" icon={<Sparkles size={16} />} />
          <FormFieldScaffold label="Autograde retries">
            <div className="app-field-value">2 retries</div>
          </FormFieldScaffold>
          <FormFieldScaffold label="Audit retention">
            <div className="app-field-value">Full term archive</div>
          </FormFieldScaffold>
        </SurfacePanel>
      </div>
    </PageShell>
  );
}

const root = ReactDOM.createRoot(document.getElementById("root")!);

root.render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
    </QueryClientProvider>
  </React.StrictMode>,
);

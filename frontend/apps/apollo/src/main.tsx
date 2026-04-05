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
  ChevronDown,
  CircleDot,
  Clock3,
  FileCode2,
  FolderOpen,
  Gauge,
  GraduationCap,
  History,
  LayoutDashboard,
  ListChecks,
  Search,
  Settings,
  Sparkles,
  Users,
} from "lucide-react";
import {
  useQuery,
} from "@tanstack/react-query";
import { brand, shellTabs, shellUtilityLinks } from "@optimark/calliope";
import "./styles.css";

type AppContext = {
  queryClient: QueryClient;
};

type StatCard = {
  label: string;
  value: string;
  context: string;
  tone?: "default" | "accent" | "alert";
};

type AssignmentRow = {
  name: string;
  type: string;
  status: string;
  due: string;
  submissions: string;
};

type ActivityItem = {
  title: string;
  when: string;
  tag?: string;
  tone?: "default" | "alert";
};

type CourseSnapshot = {
  title: string;
  term: string;
  viewLabel: string;
  stats: StatCard[];
  assignments: AssignmentRow[];
  activity: ActivityItem[];
};

const queryClient = new QueryClient();

const appSnapshot: CourseSnapshot = {
  title: brand.courseLabel,
  term: brand.courseTerm,
  viewLabel: brand.viewLabel,
  stats: [
    { label: "Drafts", value: "4", context: "Items" },
    { label: "Published", value: "12", context: "Live", tone: "accent" },
    { label: "Pending Review", value: "8", context: "Grading", tone: "alert" },
    { label: "Completed", value: "45", context: "Students" },
  ],
  assignments: [
    {
      name: "Homework 4: Linked Lists",
      type: "Practical",
      status: "Published",
      due: "Oct 12, 23:59",
      submissions: "42 / 45",
    },
    {
      name: "Assignment 3: Binary Trees",
      type: "Programming",
      status: "Reviewing",
      due: "Oct 05, 12:00",
      submissions: "45 / 45",
    },
    {
      name: "Midterm Quiz: Core Concepts",
      type: "Exam",
      status: "Draft",
      due: "Oct 24, 09:00",
      submissions: "0 / 45",
    },
    {
      name: "Homework 5: Graph Theory",
      type: "Practical",
      status: "Draft",
      due: "Nov 02, 23:59",
      submissions: "0 / 45",
    },
  ],
  activity: [
    { title: "Student A submitted Homework 4", when: "12 minutes ago" },
    {
      title: "Autograde completed for Assignment 3",
      when: "45 minutes ago",
      tag: "82% avg",
    },
    {
      title: "Manual review started on Midterm Essays",
      when: "2 hours ago",
    },
    {
      title: "System: plagiarism detected in Homework 4",
      when: "3 hours ago",
      tone: "alert",
    },
  ],
};

type AssignmentDraft = {
  title: string;
  dueDate: string;
  points: number;
  language: string;
  submissionLimit: number;
  visibility: string;
  category: string;
  description: string;
  starterFiles: { name: string; meta: string }[];
};

const assignmentDraft: AssignmentDraft = {
  title: "Homework 4: Linked Lists",
  dueDate: "Oct 15, 2026",
  points: 100,
  language: "Python 3.10+",
  submissionLimit: 3,
  visibility: "Hidden",
  category: "Coding",
  description: `## Instructions
Implement a singly linked list with the following methods:
- append(value)
- prepend(value)
- delete(value)
- find(value)

### Constraints
- Time Complexity: O(n) for searching
- Space Complexity: O(1) for deletions

Ensure all edge cases are handled (empty list, single node list).`,
  starterFiles: [
    { name: "linked_list.py", meta: "Python Source • 2.4 KB" },
    { name: "test_suite.py", meta: "Python Test • 5.1 KB" },
  ],
};

const loadSnapshot = async (): Promise<CourseSnapshot> => {
  await new Promise((resolve) => setTimeout(resolve, 60));
  return appSnapshot;
};

const loadAssignmentDraft = async (): Promise<AssignmentDraft> => {
  await new Promise((resolve) => setTimeout(resolve, 60));
  return assignmentDraft;
};

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
  component: AssignmentsOverviewPage,
});

const assignmentEditorRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/assignments/new",
  component: AssignmentEditorPage,
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
    <div className="app-frame">
      <AppSidebar />
      <div className="workspace">
        <TopBar />
        <div className="workspace-scroll">
          <Outlet />
        </div>
      </div>
    </div>
  );
}

type NavItemProps = {
  to: string;
  label: string;
  icon: React.ComponentType<{ className?: string; size?: number }>;
};

function NavItem({ to, label, icon: Icon }: NavItemProps) {
  return (
    <Link
      to={to}
      className="sidebar-link"
      activeProps={{ className: "sidebar-link sidebar-link-active" }}
    >
      <Icon className="sidebar-link-icon" size={16} />
      <span>{label}</span>
    </Link>
  );
}

function AppSidebar() {
  return (
    <aside className="sidebar">
      <div className="brand-lockup">
        <div className="brand-mark">
          <FileCode2 size={16} />
        </div>
        <div>
          <h1>{brand.name}</h1>
          <p>{brand.courseLabel}</p>
        </div>
      </div>

      <nav className="sidebar-nav">
        <NavItem to="/dashboard" label="Dashboard" icon={LayoutDashboard} />
        <NavItem to="/assignments" label="Assignments" icon={BookOpen} />
        <NavItem to="/submissions" label="Submissions" icon={ListChecks} />
        <NavItem to="/gradebook" label="Gradebook" icon={Gauge} />
        <NavItem to="/students" label="Students" icon={Users} />
        <NavItem to="/settings" label="Settings" icon={Settings} />
      </nav>

      <div className="sidebar-footer">
        <button className="primary-shell-action">New Assessment</button>
        <div className="sidebar-quiet-links">
          {shellUtilityLinks.map((item) => (
            <span key={item}>{item}</span>
          ))}
        </div>
        <div className="profile-chip">
          <div className="profile-avatar">AT</div>
          <div>
            <strong>{brand.instructorName}</strong>
            <p>{brand.instructorRole}</p>
          </div>
        </div>
      </div>
    </aside>
  );
}

function TopBar() {
  return (
    <header className="topbar">
      <nav className="topbar-links">
        {shellTabs.map((tab, index) => (
          <span key={tab} className={index === 0 ? "topbar-active" : undefined}>
            {tab}
          </span>
        ))}
      </nav>

      <div className="topbar-tools">
        <label className="search-shell">
          <Search size={14} />
          <input placeholder="Search assessments..." />
        </label>
        <button className="icon-button" aria-label="Notifications">
          <Bell size={16} />
        </button>
        <button className="icon-button" aria-label="History">
          <History size={16} />
        </button>
        <div className="profile-avatar profile-avatar-small">AT</div>
      </div>
    </header>
  );
}

function PageHeader(props: {
  eyebrow?: string;
  title: string;
  subtitle?: string;
  actions?: React.ReactNode;
}) {
  return (
    <div className="page-header">
      <div>
        {props.eyebrow ? <p className="eyebrow">{props.eyebrow}</p> : null}
        <h2>{props.title}</h2>
        {props.subtitle ? <p className="page-subtitle">{props.subtitle}</p> : null}
      </div>
      {props.actions ? <div className="page-actions">{props.actions}</div> : null}
    </div>
  );
}

function DashboardPage() {
  const { data } = useQuery({
    queryKey: ["course-snapshot"],
    queryFn: loadSnapshot,
  });

  if (!data) {
    return <PageSkeleton title="Loading dashboard..." />;
  }

  return (
    <section className="page-shell">
      <PageHeader
        title={data.title}
        subtitle={`${data.term} • ${data.viewLabel}`}
        actions={
          <>
            <button className="secondary-shell-action">Open Gradebook</button>
            <button className="primary-shell-action">Publish All</button>
          </>
        }
      />

      <div className="stats-grid">
        {data.stats.map((stat) => (
          <article key={stat.label} className="stat-panel">
            <span className={`stat-label stat-label-${stat.tone ?? "default"}`}>
              {stat.label}
            </span>
            <div className="stat-row">
              <strong>{stat.value}</strong>
              <span>{stat.context}</span>
            </div>
          </article>
        ))}
      </div>

      <div className="content-grid">
        <section className="surface-panel panel-large">
          <div className="panel-heading">
            <h3>Active Coursework</h3>
            <button className="inline-action">
              Filter
              <ChevronDown size={14} />
            </button>
          </div>

          <div className="table-shell">
            <table>
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
                {data.assignments.map((row) => (
                  <tr key={row.name}>
                    <td className="cell-strong">{row.name}</td>
                    <td>{row.type}</td>
                    <td>
                      <span className={`status-pill status-${row.status.toLowerCase()}`}>
                        {row.status}
                      </span>
                    </td>
                    <td>{row.due}</td>
                    <td className="align-right">{row.submissions}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <aside className="surface-panel panel-activity">
          <div className="panel-heading">
            <h3>Operational Feed</h3>
            <Sparkles size={14} />
          </div>

          <div className="activity-list">
            {data.activity.map((item) => (
              <article key={item.title} className="activity-item">
                <div className={`activity-mark activity-${item.tone ?? "default"}`}>
                  <CircleDot size={14} />
                </div>
                <div>
                  <strong>{item.title}</strong>
                  <p>{item.when}</p>
                  {item.tag ? <span className="activity-tag">{item.tag}</span> : null}
                </div>
              </article>
            ))}
          </div>
        </aside>
      </div>
    </section>
  );
}

function AssignmentEditorPage() {
  const { data } = useQuery({
    queryKey: ["assignment-draft"],
    queryFn: loadAssignmentDraft,
  });

  if (!data) {
    return <PageSkeleton title="Loading assignment editor..." />;
  }

  return (
    <section className="page-shell">
      <PageHeader
        eyebrow="Assignment Editor"
        title={data.title}
        actions={
          <>
            <button className="secondary-shell-action">Save Draft</button>
            <button className="primary-shell-action">Publish</button>
          </>
        }
      />

      <div className="editor-grid">
        <section className="editor-main">
          <div className="section-heading">
            <h3>Description</h3>
            <div className="toggle-set">
              <span className="toggle-active">Write</span>
              <span>Preview</span>
            </div>
          </div>

          <div className="editor-surface">
            <pre>{data.description}</pre>
          </div>

          <div className="section-heading">
            <h3>Starter Files</h3>
          </div>

          <div className="file-stack">
            {data.starterFiles.map((file) => (
              <div key={file.name} className="file-row">
                <div className="file-row-main">
                  <FolderOpen size={16} />
                  <div>
                    <strong>{file.name}</strong>
                    <p>{file.meta}</p>
                  </div>
                </div>
              </div>
            ))}
            <button className="upload-shell">Upload Additional Files</button>
          </div>
        </section>

        <aside className="surface-panel editor-sidebar">
          <div className="panel-heading">
            <h3>Metadata</h3>
          </div>

          <div className="meta-grid">
            <MetaField label="Due Date" value={data.dueDate} />
            <MetaField label="Points" value={String(data.points)} />
            <MetaField label="Language" value={data.language} />
            <MetaField label="Submission Limit" value={String(data.submissionLimit)} />
            <MetaField label="Visibility" value={data.visibility} />
            <MetaField label="Category" value={data.category} />
          </div>

          <div className="verify-panel">
            <Settings size={18} />
            <strong>Verify Environment</strong>
            <p>Confirm dependencies, runner config, and starter files before publishing.</p>
          </div>
        </aside>
      </div>
    </section>
  );
}

function AssignmentsOverviewPage() {
  return (
    <PlaceholderPage
      title="Assignments"
      subtitle="Use this route group for future assignment lists, creation flows, and publishing controls."
      actionLabel="Open Editor"
      actionTo="/assignments/new"
    />
  );
}

function SubmissionsPage() {
  return (
    <PlaceholderPage
      title="Submissions"
      subtitle="This route is ready for queue views, processing states, and review-focused assignment drilldowns."
    />
  );
}

function GradebookPage() {
  return (
    <PlaceholderPage
      title="Gradebook"
      subtitle="This shell is ready for dense table layouts, grade-release workflows, and student-by-assignment summaries."
    />
  );
}

function StudentsPage() {
  return (
    <PlaceholderPage
      title="Students"
      subtitle="Future roster, enrollment, and per-student activity surfaces can plug into the shared shell here."
    />
  );
}

function SettingsPage() {
  return (
    <PlaceholderPage
      title="Settings"
      subtitle="Use this area for course configuration, grading policies, integrations, and audit-oriented controls."
    />
  );
}

function PlaceholderPage(props: {
  title: string;
  subtitle: string;
  actionLabel?: string;
  actionTo?: string;
}) {
  return (
    <section className="page-shell">
      <PageHeader
        title={props.title}
        subtitle={props.subtitle}
        actions={
          props.actionLabel && props.actionTo ? (
            <Link to={props.actionTo} className="primary-shell-action">
              {props.actionLabel}
            </Link>
          ) : undefined
        }
      />

      <div className="placeholder-surface">
        <GraduationCap size={18} />
        <p>
          Shared app shell, routing, and styling are wired. This screen is a lightweight
          placeholder for issue-focused product work to land next.
        </p>
      </div>
    </section>
  );
}

function MetaField(props: { label: string; value: string }) {
  return (
    <div className="meta-field">
      <span>{props.label}</span>
      <strong>{props.value}</strong>
    </div>
  );
}

function PageSkeleton(props: { title: string }) {
  return (
    <section className="page-shell">
      <PageHeader title={props.title} subtitle="Preparing workspace..." />
      <div className="placeholder-surface">
        <Clock3 size={18} />
        <p>Loading mock data and shared workspace context.</p>
      </div>
    </section>
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

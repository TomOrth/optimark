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
  Clock3,
  FileCode2,
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
import { useQuery } from "@tanstack/react-query";
import { brand, shellTabs, shellUtilityLinks } from "@optimark/calliope";
import "./styles.css";

type AppContext = {
  queryClient: QueryClient;
};

type FoundationMetric = {
  label: string;
  value: string;
  context: string;
  tone?: "default" | "accent" | "alert";
};

type ScaffoldRoute = {
  path: string;
  summary: string;
  status: "ready" | "planned" | "stub";
};

type FoundationPattern = {
  title: string;
  description: string;
};

type FoundationOverview = {
  title: string;
  subtitle: string;
  metrics: FoundationMetric[];
  routes: ScaffoldRoute[];
  patterns: FoundationPattern[];
};

const queryClient = new QueryClient();

const foundationOverview: FoundationOverview = {
  title: `${brand.name} Shell`,
  subtitle: "Router, query, package boundaries, and shared shell primitives are wired for future product tickets.",
  metrics: [
    { label: "Routes", value: "7", context: "Scaffolded", tone: "accent" },
    { label: "Query", value: "1", context: "Provider" },
    { label: "Packages", value: "2", context: "Apollo + Calliope" },
    { label: "Status", value: "Ready", context: "Bootstrap", tone: "alert" },
  ],
  routes: [
    {
      path: "/dashboard",
      summary: "Shell preview and shared foundation patterns.",
      status: "ready",
    },
    {
      path: "/assignments",
      summary: "Reserved for issue #8 assignment management flows.",
      status: "planned",
    },
    {
      path: "/assignments/new",
      summary: "Reserved route for the future assignment builder entrypoint.",
      status: "stub",
    },
    {
      path: "/submissions",
      summary: "Reserved for student submission and processing work.",
      status: "planned",
    },
    {
      path: "/gradebook",
      summary: "Reserved for instructor and student read-oriented grade views.",
      status: "planned",
    },
    {
      path: "/students",
      summary: "Reserved for roster and per-student workflow surfaces.",
      status: "planned",
    },
    {
      path: "/settings",
      summary: "Reserved for course configuration and policy controls.",
      status: "planned",
    },
  ],
  patterns: [
    {
      title: "App Shell",
      description: "Persistent sidebar, sticky top bar, and centered workspace canvas are ready for authenticated flows.",
    },
    {
      title: "Page Primitives",
      description: "Page headers, actions, placeholder states, and surface panels are available for future screens.",
    },
    {
      title: "State Styling",
      description: "Status pills, loading states, and restrained surface treatments provide a consistent baseline.",
    },
    {
      title: "Package Boundaries",
      description: "Apollo owns the app runtime while Calliope owns shared brand and shell definitions.",
    },
  ],
};

const loadFoundationOverview = async (): Promise<FoundationOverview> => {
  await new Promise((resolve) => setTimeout(resolve, 60));
  return foundationOverview;
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
  component: FoundationPreviewPage,
});

const assignmentsRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/assignments",
  component: AssignmentsOverviewPage,
});

const assignmentEditorRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/assignments/new",
  component: AssignmentBuilderRoutePage,
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

function FoundationPreviewPage() {
  const { data } = useQuery({
    queryKey: ["foundation-overview"],
    queryFn: loadFoundationOverview,
  });

  if (!data) {
    return <PageSkeleton title="Loading shell preview..." />;
  }

  return (
    <section className="page-shell">
      <PageHeader
        title={data.title}
        subtitle={data.subtitle}
        actions={
          <>
            <button className="secondary-shell-action">Secondary Action</button>
            <button className="primary-shell-action">Primary Action</button>
          </>
        }
      />

      <div className="stats-grid">
        {data.metrics.map((stat) => (
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
            <h3>Route Map</h3>
            <span className="inline-action">Shared Scaffold</span>
          </div>

          <div className="table-shell">
            <table>
              <thead>
                <tr>
                  <th>Path</th>
                  <th>Purpose</th>
                  <th className="align-right">Status</th>
                </tr>
              </thead>
              <tbody>
                {data.routes.map((route) => (
                  <tr key={route.path}>
                    <td className="cell-strong">{route.path}</td>
                    <td>{route.summary}</td>
                    <td className="align-right">
                      <span className={`status-pill status-${route.status}`}>
                        {route.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <aside className="surface-panel panel-activity">
          <div className="panel-heading">
            <h3>Foundation Patterns</h3>
            <Sparkles size={14} />
          </div>

          <div className="activity-list">
            {data.patterns.map((item) => (
              <article key={item.title} className="activity-item">
                <div className="activity-mark">
                  <Sparkles size={14} />
                </div>
                <div>
                  <strong>{item.title}</strong>
                  <p>{item.description}</p>
                </div>
              </article>
            ))}
          </div>
        </aside>
      </div>
    </section>
  );
}

function AssignmentBuilderRoutePage() {
  return (
    <PlaceholderPage
      title="Assignment Builder Route"
      subtitle="This route is reserved for the future assignment editor flow in issue #8."
    />
  );
}

function AssignmentsOverviewPage() {
  return (
    <PlaceholderPage
      title="Assignments"
      subtitle="Use this route group for future assignment lists, creation flows, and publishing controls."
      actionLabel="Open Reserved Builder Route"
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

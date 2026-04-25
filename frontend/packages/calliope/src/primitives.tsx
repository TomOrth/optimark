/** Reusable shell and UI primitives for the Optimark frontend workspace. */

import type { HTMLAttributes, ReactNode } from "react";

export type ShellBrandProps = {
  name: string;
  context: string;
  mark: ReactNode;
};

export function BrandLockup({ name, context, mark }: ShellBrandProps) {
  return (
    <div className="calliope-brand-lockup">
      <div className="calliope-brand-mark">{mark}</div>
      <div>
        <h1>{name}</h1>
        <p>{context}</p>
      </div>
    </div>
  );
}

type SidebarShellProps = {
  brand: ReactNode;
  navigation: ReactNode;
  primaryAction?: ReactNode;
  utilityLinks?: ReactNode;
  profile?: ReactNode;
};

export function SidebarShell({
  brand,
  navigation,
  primaryAction,
  utilityLinks,
  profile,
}: SidebarShellProps) {
  return (
    <aside className="calliope-sidebar">
      {brand}
      <nav className="calliope-sidebar-nav">{navigation}</nav>
      <div className="calliope-sidebar-footer">
        {primaryAction}
        {utilityLinks ? (
          <div className="calliope-sidebar-utility">{utilityLinks}</div>
        ) : null}
        {profile}
      </div>
    </aside>
  );
}

type SidebarNavItemProps = {
  active?: boolean;
  icon: ReactNode;
  label: string;
  trailing?: ReactNode;
} & HTMLAttributes<HTMLDivElement>;

export function SidebarNavItem({
  active = false,
  icon,
  label,
  trailing,
  className = "",
  ...props
}: SidebarNavItemProps) {
  return (
    <div
      className={`calliope-sidebar-link ${active ? "calliope-sidebar-link-active" : ""} ${className}`.trim()}
      {...props}
    >
      <span className="calliope-sidebar-link-icon">{icon}</span>
      <span>{label}</span>
      {trailing ? <span>{trailing}</span> : null}
    </div>
  );
}

type TopbarProps = {
  tabs?: ReactNode;
  search?: ReactNode;
  tools?: ReactNode;
  actions?: ReactNode;
};

export function Topbar({ tabs, search, tools, actions }: TopbarProps) {
  return (
    <header className="calliope-topbar">
      <div className="calliope-topbar-tabs">{tabs}</div>
      <div className="calliope-topbar-right">
        {search}
        {tools}
        {actions}
      </div>
    </header>
  );
}

type TopbarTabProps = {
  active?: boolean;
  children: ReactNode;
} & HTMLAttributes<HTMLButtonElement>;

export function TopbarTab({
  active = false,
  children,
  className = "",
  ...props
}: TopbarTabProps) {
  return (
    <button
      className={`calliope-topbar-tab ${active ? "calliope-topbar-tab-active" : ""} ${className}`.trim()}
      type="button"
      {...props}
    >
      {children}
    </button>
  );
}

type AppFrameProps = {
  sidebar: ReactNode;
  topbar: ReactNode;
  children: ReactNode;
};

export function AppFrame({ sidebar, topbar, children }: AppFrameProps) {
  return (
    <div className="calliope-app-frame">
      {sidebar}
      <div className="calliope-workspace">
        {topbar}
        <div className="calliope-workspace-scroll">{children}</div>
      </div>
    </div>
  );
}

type PageShellProps = {
  children: ReactNode;
};

export function PageShell({ children }: PageShellProps) {
  return <section className="calliope-page-shell">{children}</section>;
}

type PageHeaderProps = {
  eyebrow?: string;
  title: string;
  subtitle?: string;
  actions?: ReactNode;
};

export function PageHeader({
  eyebrow,
  title,
  subtitle,
  actions,
}: PageHeaderProps) {
  return (
    <div className="calliope-page-header">
      <div>
        {eyebrow ? <p className="calliope-eyebrow">{eyebrow}</p> : null}
        <h2>{title}</h2>
        {subtitle ? <p className="calliope-page-subtitle">{subtitle}</p> : null}
      </div>
      {actions ? <div className="calliope-page-actions">{actions}</div> : null}
    </div>
  );
}

type SurfacePanelProps = {
  children: ReactNode;
  muted?: boolean;
  className?: string;
};

export function SurfacePanel({
  children,
  muted = false,
  className = "",
}: SurfacePanelProps) {
  return (
    <div
      className={`calliope-surface-panel ${muted ? "calliope-surface-panel-muted" : ""} ${className}`.trim()}
    >
      {children}
    </div>
  );
}

type SectionHeadingProps = {
  icon?: ReactNode;
  title: string;
  actions?: ReactNode;
};

export function SectionHeading({
  icon,
  title,
  actions,
}: SectionHeadingProps) {
  return (
    <div className="calliope-section-heading">
      <h3>
        {icon ? <span className="calliope-section-heading-icon">{icon}</span> : null}
        {title}
      </h3>
      {actions}
    </div>
  );
}

type MetricCardProps = {
  label: string;
  value: string;
  context?: string;
  tone?: "default" | "primary" | "danger";
};

export function MetricCard({
  label,
  value,
  context,
  tone = "default",
}: MetricCardProps) {
  return (
    <article className="calliope-metric-card">
      <span className={`calliope-metric-label calliope-tone-${tone}`}>{label}</span>
      <div className="calliope-metric-row">
        <strong>{value}</strong>
        {context ? <span>{context}</span> : null}
      </div>
    </article>
  );
}

type StatusPillProps = {
  tone?: "default" | "primary" | "secondary" | "danger";
  children: ReactNode;
};

export function StatusPill({
  tone = "default",
  children,
}: StatusPillProps) {
  return (
    <span className={`calliope-status-pill calliope-status-${tone}`}>
      {children}
    </span>
  );
}

type EmptyStateProps = {
  icon?: ReactNode;
  title: string;
  description: string;
  action?: ReactNode;
};

export function EmptyState({
  icon,
  title,
  description,
  action,
}: EmptyStateProps) {
  return (
    <SurfacePanel className="calliope-empty-state">
      {icon ? <div className="calliope-empty-icon">{icon}</div> : null}
      <div>
        <strong>{title}</strong>
        <p>{description}</p>
      </div>
      {action}
    </SurfacePanel>
  );
}

type FormFieldProps = {
  label: string;
  support?: string;
  children: ReactNode;
};

export function FormFieldScaffold({
  label,
  support,
  children,
}: FormFieldProps) {
  return (
    <label className="calliope-form-field">
      <span className="calliope-form-label">{label}</span>
      {children}
      {support ? <span className="calliope-form-support">{support}</span> : null}
    </label>
  );
}

type BottomActionBarProps = {
  leading?: ReactNode;
  actions: ReactNode;
};

export function BottomActionBar({
  leading,
  actions,
}: BottomActionBarProps) {
  return (
    <div className="calliope-bottom-action-bar">
      {leading ? <div className="calliope-bottom-leading">{leading}</div> : null}
      <div className="calliope-bottom-actions">{actions}</div>
    </div>
  );
}

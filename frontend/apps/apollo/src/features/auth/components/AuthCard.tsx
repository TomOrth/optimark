import type { ReactNode } from "react";

import { SurfacePanel } from "@optimark/calliope";

export function AuthCard({
  eyebrow,
  title,
  subtitle,
  children,
  footer,
}: {
  eyebrow: string;
  title: string;
  subtitle: string;
  children: ReactNode;
  footer?: ReactNode;
}) {
  return (
    <SurfacePanel className="app-auth-card">
      <div className="app-auth-card-header">
        <span className="app-smallcaps">{eyebrow}</span>
        <h1>{title}</h1>
        <p>{subtitle}</p>
      </div>
      {children}
      {footer}
    </SurfacePanel>
  );
}

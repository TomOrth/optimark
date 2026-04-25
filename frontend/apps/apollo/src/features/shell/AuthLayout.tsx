import { Outlet } from "@tanstack/react-router";
import { Code2 } from "lucide-react";
import { BrandLockup, SurfacePanel, brand } from "@optimark/calliope";

export function AuthLayout() {
  return (
    <div className="app-auth-shell">
      <div className="app-auth-background" />
      <div className="app-auth-grid">
        <section className="app-auth-story">
          <BrandLockup
            name={brand.name}
            context={`${brand.courseLabel} • ${brand.courseTerm}`}
            mark={<Code2 size={18} />}
          />
          <div className="app-auth-copy">
            <span className="app-smallcaps">Hosted Access</span>
            <h2>The academic workspace with operational calm.</h2>
            <p>
              Sign in to restore your course session, review assessment activity,
              and continue in the same curated shell used across the app.
            </p>
          </div>
          <div className="app-auth-highlights">
            <SurfacePanel muted className="app-auth-note">
              <strong>Session restoration</strong>
              <p>Cookie-backed app access restores your workspace on reload.</p>
            </SurfacePanel>
            <SurfacePanel muted className="app-auth-note">
              <strong>Protected surfaces</strong>
              <p>Instructor and student routes stay gated until a valid session exists.</p>
            </SurfacePanel>
          </div>
        </section>
        <div className="app-auth-panel">
          <Outlet />
        </div>
      </div>
    </div>
  );
}

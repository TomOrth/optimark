import { Link } from "@tanstack/react-router";
import { FolderOpen } from "lucide-react";
import { EmptyState, PageHeader, PageShell } from "@optimark/calliope";

export function AssignmentsPage() {
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

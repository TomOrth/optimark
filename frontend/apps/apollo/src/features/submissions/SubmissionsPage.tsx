import { ListChecks } from "lucide-react";
import { EmptyState, PageHeader, PageShell } from "@optimark/calliope";

export function SubmissionsPage() {
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

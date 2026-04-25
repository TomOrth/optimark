import { GraduationCap } from "lucide-react";
import { EmptyState, PageHeader, PageShell } from "@optimark/calliope";

export function StudentsPage() {
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

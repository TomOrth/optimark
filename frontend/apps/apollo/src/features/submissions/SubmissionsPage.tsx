import { useQuery } from "@tanstack/react-query";
import { Link } from "@tanstack/react-router";
import { ChevronRight, FileCode2, LoaderCircle } from "lucide-react";
import { EmptyState, PageHeader, PageShell } from "@optimark/calliope";

import {
  fetchStudentAssignments,
  type StudentAssignmentSummary,
  type SubmissionLifecycleStatus,
} from "./api";

const statusCopy: Record<SubmissionLifecycleStatus, string> = {
  draft: "Draft",
  submitted: "Submitted",
  queued: "Queued",
  running: "Running",
  completed: "Completed",
  failed: "Failed",
  withdrawn: "Withdrawn",
};

export function SubmissionsPage() {
  const assignments = useQuery({
    queryKey: ["student", "assignments"],
    queryFn: fetchStudentAssignments,
  });
  const assignmentItems = assignments.data ?? [];

  return (
    <PageShell>
      <PageHeader
        eyebrow="Student Workspace"
        title="Coding submissions"
        subtitle="Open any assigned coding task, upload the required archive, and track whether it is still a draft or moving through autograde."
      />

      {assignments.isLoading ? (
        <section className="app-overview-card">
          <div className="app-loading-row">
            <LoaderCircle className="app-spin" size={18} />
            <span>Loading your assigned coding tasks...</span>
          </div>
        </section>
      ) : assignments.isError ? (
        <section className="app-overview-card">
          <p className="app-error-copy">{assignments.error.message}</p>
        </section>
      ) : assignmentItems.length === 0 ? (
        <EmptyState
          icon={<FileCode2 size={18} />}
          title="No coding assignments are ready yet"
          description="Published coding work will appear here as soon as your course staff assigns it."
        />
      ) : (
        <section className="app-submission-card-grid">
          {assignmentItems.map((item) => (
            <AssignmentCard key={item.assignment.id} item={item} />
          ))}
        </section>
      )}
    </PageShell>
  );
}

function AssignmentCard({ item }: { item: StudentAssignmentSummary }) {
  const latestStatus = item.latest_submission?.lifecycle_status;

  return (
    <article className="app-overview-card app-submission-card">
      <div className="app-submission-card-header">
        <div>
          <span className="app-smallcaps">
            {item.course.course_code} • {item.course.term}
          </span>
          <h3>{item.assignment.title}</h3>
          <p>{item.assignment.description}</p>
        </div>
        <span
          className={`app-status-badge ${
            latestStatus ? `app-status-${latestStatus}` : "app-status-none"
          }`}
        >
          {latestStatus ? statusCopy[latestStatus] : "Not started"}
        </span>
      </div>

      <div className="app-submission-meta-grid">
        <div>
          <span className="app-smallcaps">Latest artifact</span>
          <strong>{item.latest_submission?.artifact_name ?? "Nothing uploaded yet"}</strong>
        </div>
        <div>
          <span className="app-smallcaps">Last activity</span>
          <strong>{formatDateTime(item.latest_submission?.updated_at)}</strong>
        </div>
      </div>

      <Link
        to="/submissions/$courseId/$assignmentId"
        params={{
          courseId: item.course.id,
          assignmentId: item.assignment.id,
        }}
        className="app-primary-action"
      >
        Open submission task
        <ChevronRight size={16} />
      </Link>
    </article>
  );
}

function formatDateTime(value?: string | null): string {
  if (!value) {
    return "No submission activity";
  }

  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

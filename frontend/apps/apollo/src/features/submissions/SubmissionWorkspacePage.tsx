import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link } from "@tanstack/react-router";
import { startTransition, useState } from "react";
import { FileArchive, LoaderCircle, Upload } from "lucide-react";
import { PageHeader, PageShell } from "@optimark/calliope";

import {
  createSubmission,
  fetchSubmissionWorkspace,
  type StudentSubmissionRecord,
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

export function SubmissionWorkspacePage(props: {
  courseId: string;
  assignmentId: string;
}) {
  const queryClient = useQueryClient();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const workspace = useQuery({
    queryKey: ["student", "submission-workspace", props.courseId, props.assignmentId],
    queryFn: () => fetchSubmissionWorkspace(props.courseId, props.assignmentId),
  });

  const uploadSubmission = useMutation({
    mutationFn: (state: "draft" | "submitted") => {
      if (!selectedFile) {
        throw new Error("Choose a file or archive before uploading.");
      }

      return createSubmission({
        courseId: props.courseId,
        assignmentId: props.assignmentId,
        file: selectedFile,
        state,
      });
    },
    onSuccess: async () => {
      startTransition(() => {
        setSelectedFile(null);
      });
      await Promise.all([
        queryClient.invalidateQueries({
          queryKey: ["student", "submission-workspace", props.courseId, props.assignmentId],
        }),
        queryClient.invalidateQueries({
          queryKey: ["student", "assignments"],
        }),
      ]);
    },
  });

  if (workspace.isLoading) {
    return (
      <PageShell>
        <PageHeader
          eyebrow="Student Workspace"
          title="Loading submission task"
          subtitle="Pulling the latest assignment instructions and submission history."
        />
        <section className="app-overview-card">
          <div className="app-loading-row">
            <LoaderCircle className="app-spin" size={18} />
            <span>Loading assignment workspace...</span>
          </div>
        </section>
      </PageShell>
    );
  }

  if (workspace.isError) {
    return (
      <PageShell>
        <PageHeader
          eyebrow="Student Workspace"
          title="Submission task unavailable"
          subtitle="This assignment may no longer be published for student submission."
        />
        <section className="app-overview-card">
          <p className="app-error-copy">{workspace.error.message}</p>
          <Link to="/submissions" className="app-secondary-action">
            Back to submissions
          </Link>
        </section>
      </PageShell>
    );
  }

  const workspaceData = workspace.data;
  if (!workspaceData) {
    return null;
  }

  const { assignment, course, submissions } = workspaceData;

  return (
    <PageShell>
      <PageHeader
        eyebrow={`${course.course_code} • ${course.term}`}
        title={assignment.title}
        subtitle={assignment.description}
        actions={
          <Link to="/submissions" className="app-secondary-action">
            Back to all submissions
          </Link>
        }
      />

      <div className="app-editor-grid">
        <div className="app-editor-main">
          <section className="app-editor-block">
            <span className="app-smallcaps">Upload required files</span>
            <div className="app-submission-upload-panel">
              <label className="app-upload-zone app-upload-zone-input">
                <input
                  type="file"
                  onChange={(event) => {
                    const nextFile = event.target.files?.[0] ?? null;
                    startTransition(() => {
                      setSelectedFile(nextFile);
                    });
                  }}
                />
                <Upload size={18} />
                <span>{selectedFile ? selectedFile.name : "Choose file or archive"}</span>
              </label>

              <div className="app-submission-meta-grid">
                <div>
                  <span className="app-smallcaps">Selected</span>
                  <strong>{selectedFile?.name ?? "No file selected"}</strong>
                </div>
                <div>
                  <span className="app-smallcaps">Size</span>
                  <strong>{selectedFile ? formatFileSize(selectedFile.size) : "Awaiting upload"}</strong>
                </div>
              </div>

              {uploadSubmission.isError ? (
                <p className="app-error-copy">{uploadSubmission.error.message}</p>
              ) : null}

              <div className="app-submission-action-row">
                <button
                  type="button"
                  className="app-secondary-action"
                  disabled={!selectedFile || uploadSubmission.isPending}
                  onClick={() => uploadSubmission.mutate("draft")}
                >
                  Save draft
                </button>
                <button
                  type="button"
                  className="app-primary-action"
                  disabled={!selectedFile || uploadSubmission.isPending}
                  onClick={() => uploadSubmission.mutate("submitted")}
                >
                  {uploadSubmission.isPending ? "Uploading..." : "Submit for grading"}
                </button>
              </div>
            </div>
          </section>

          <section className="app-table-panel">
            <div className="app-submission-section-header">
              <div>
                <span className="app-smallcaps">Submission history</span>
                <h3>Your uploads and current status</h3>
              </div>
            </div>

            {submissions.length === 0 ? (
              <p className="app-empty-copy">
                No artifacts uploaded yet. Save a draft first if you want to checkpoint work
                before submitting.
              </p>
            ) : (
              <div className="app-submission-history">
                {submissions.map((submission: StudentSubmissionRecord) => (
                  <SubmissionHistoryItem key={submission.id} submission={submission} />
                ))}
              </div>
            )}
          </section>
        </div>

        <aside className="app-editor-inspector">
          <section className="app-settings-panel">
            <span className="app-smallcaps">Submission rules</span>
            <div className="app-status-cluster">
              <strong>Single-upload MVP</strong>
              <p>Upload the required file or archive. Drafts stay private to you until you submit.</p>
            </div>
            <div className="app-status-cluster">
              <strong>Autograde-compatible</strong>
              <p>Submitted artifacts move into a queued state immediately so a later worker can pick them up.</p>
            </div>
          </section>
        </aside>
      </div>
    </PageShell>
  );
}

function SubmissionHistoryItem(props: { submission: StudentSubmissionRecord }) {
  const { submission } = props;

  return (
    <article className="app-submission-history-item">
      <div className="app-submission-history-main">
        <div className="app-file-main">
          <FileArchive className="app-file-icon" size={18} />
          <div>
            <strong>{submission.artifact_name ?? "Uploaded artifact"}</strong>
            <p>{formatDateTime(submission.updated_at)}</p>
          </div>
        </div>
        <span className={`app-status-badge app-status-${submission.lifecycle_status}`}>
          {statusCopy[submission.lifecycle_status]}
        </span>
      </div>
      <p className="app-submission-detail-copy">
        {submission.submitted_at
          ? `Submitted ${formatDateTime(submission.submitted_at)}`
          : "Saved as draft and not yet submitted for grading."}
      </p>
    </article>
  );
}

function formatDateTime(value: string): string {
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

function formatFileSize(size: number): string {
  if (size < 1024) {
    return `${size} B`;
  }
  if (size < 1024 * 1024) {
    return `${(size / 1024).toFixed(1)} KB`;
  }
  return `${(size / (1024 * 1024)).toFixed(1)} MB`;
}

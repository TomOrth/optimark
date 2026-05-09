import { useEffect, useMemo, useState } from "react";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useNavigate } from "@tanstack/react-router";
import { CircleAlert, FileCode2, FolderOpen, LoaderCircle, Sparkles } from "lucide-react";
import {
  BottomActionBar,
  EmptyState,
  FormFieldScaffold,
  PageHeader,
  PageShell,
  SectionHeading,
  StatusPill,
  SurfacePanel,
} from "@optimark/calliope";

import {
  assignmentDetailQueryKey,
  createAssignment,
  fetchAssignmentDetail,
  fetchManagedCourses,
  managedAssignmentsQueryKey,
  managedCoursesQueryKey,
  sanitizeCourseId,
  updateAssignment,
  type AssignmentPublishState,
  type AssignmentType,
} from "./api";

type AssignmentBuilderPageProps = {
  mode: "create" | "edit";
  assignmentId?: string;
  courseId?: string;
};

type AssignmentFormState = {
  title: string;
  description: string;
  assignmentType: AssignmentType;
  publishState: AssignmentPublishState;
};

const INITIAL_FORM_STATE: AssignmentFormState = {
  title: "",
  description: "",
  assignmentType: "coding",
  publishState: "draft",
};

export function AssignmentBuilderPage({
  mode,
  assignmentId,
  courseId,
}: AssignmentBuilderPageProps) {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const [formState, setFormState] = useState<AssignmentFormState>(INITIAL_FORM_STATE);
  const normalizedCourseId = sanitizeCourseId(courseId);

  const coursesQuery = useQuery({
    queryKey: managedCoursesQueryKey,
    queryFn: fetchManagedCourses,
  });

  const selectedCourseId = useMemo(
    () =>
      mode === "edit"
        ? normalizedCourseId
        : normalizedCourseId ?? coursesQuery.data?.[0]?.id,
    [coursesQuery.data, mode, normalizedCourseId],
  );

  const selectedCourse =
    coursesQuery.data?.find((course) => course.id === selectedCourseId) ?? null;

  const assignmentDetailQuery = useQuery({
    queryKey:
      mode === "edit" && selectedCourseId && assignmentId
        ? assignmentDetailQueryKey(selectedCourseId, assignmentId)
        : ["instructor", "assignments", "editor", "unselected"],
    queryFn: () => fetchAssignmentDetail(selectedCourseId!, assignmentId!),
    enabled: mode === "edit" && Boolean(selectedCourseId) && Boolean(assignmentId),
  });

  useEffect(() => {
    if (mode === "edit" && assignmentDetailQuery.data) {
      setFormState({
        title: assignmentDetailQuery.data.title,
        description: assignmentDetailQuery.data.description,
        assignmentType: assignmentDetailQuery.data.assignmentType,
        publishState: assignmentDetailQuery.data.publishState,
      });
      return;
    }

    if (mode === "create") {
      setFormState(INITIAL_FORM_STATE);
    }
  }, [assignmentDetailQuery.data, mode]);

  useEffect(() => {
    if (
      mode === "create" &&
      selectedCourseId &&
      selectedCourseId !== normalizedCourseId
    ) {
      void navigate({
        to: ".",
        search: { course: selectedCourseId },
        replace: true,
      });
    }
  }, [mode, navigate, normalizedCourseId, selectedCourseId]);

  const assignmentMutation = useMutation({
    mutationFn: async (nextState: AssignmentFormState) => {
      if (!selectedCourseId) {
        throw new Error("Select a managed course before saving an assignment.");
      }

      if (mode === "edit" && assignmentId) {
        return updateAssignment(selectedCourseId, assignmentId, nextState);
      }

      return createAssignment(selectedCourseId, nextState);
    },
    onSuccess: async (assignment) => {
      if (!selectedCourseId) {
        return;
      }

      await queryClient.invalidateQueries({
        queryKey: managedAssignmentsQueryKey(selectedCourseId),
      });
      queryClient.setQueryData(
        assignmentDetailQueryKey(selectedCourseId, assignment.id),
        assignment,
      );
      await navigate({
        to: "/courses/$courseId/assignments/$assignmentId",
        params: { assignmentId: assignment.id, courseId: selectedCourseId },
        replace: mode === "edit",
      });
    },
  });

  const isLoading =
    coursesQuery.isLoading || (mode === "edit" && assignmentDetailQuery.isLoading);
  const loadError =
    coursesQuery.error instanceof Error
      ? coursesQuery.error
      : assignmentDetailQuery.error instanceof Error
        ? assignmentDetailQuery.error
        : null;

  const editorTitle =
    mode === "edit" ? formState.title || "Edit Assignment" : "Create Assignment";

  const submitWithState = (publishState: AssignmentPublishState) => {
    assignmentMutation.mutate({
      ...formState,
      publishState,
    });
  };

  const handleCourseChange = (nextCourseId: string) => {
    if (mode === "edit" && assignmentId) {
      void navigate({
        to: "/courses/$courseId/assignments/$assignmentId",
        params: { assignmentId, courseId: nextCourseId },
      });
      return;
    }

    void navigate({
      to: "/assignments/new",
      search: { course: nextCourseId },
    });
  };

  if (isLoading) {
    return (
      <PageShell>
        <PageHeader eyebrow="Assignment Editor" title="Loading assignment workspace" />
        <SurfacePanel className="app-panel-state">
          <LoaderCircle size={18} className="app-spin" />
          <span>Preparing the assignment editor...</span>
        </SurfacePanel>
      </PageShell>
    );
  }

  if (loadError) {
    return (
      <PageShell>
        <PageHeader eyebrow="Assignment Editor" title="We hit a loading problem" />
        <SurfacePanel className="app-panel-state app-panel-state-error">
          <CircleAlert size={18} />
          <span>{loadError.message}</span>
        </SurfacePanel>
      </PageShell>
    );
  }

  if (!selectedCourseId || !selectedCourse) {
    return (
      <PageShell>
        <PageHeader
          eyebrow="Assignment Editor"
          title="No managed course selected"
          subtitle="Choose one of your managed courses before creating assignments."
        />
        <EmptyState
          icon={<FolderOpen size={18} />}
          title="Managed courses required"
          description="Return to the assignments overview to pick a course context for this editor."
          action={
            <Link to="/assignments" search={{ course: undefined }} className="app-primary-action">
              Back to Assignments
            </Link>
          }
        />
      </PageShell>
    );
  }

  return (
    <PageShell>
      <PageHeader
        eyebrow={mode === "edit" ? "Edit Assignment" : "Create Assignment"}
        title={editorTitle}
        subtitle={`${selectedCourse.courseCode} • ${selectedCourse.title}`}
      />

      <div className="app-editor-grid">
        <div className="app-editor-main">
          <SectionHeading
            icon={<FileCode2 size={16} />}
            title="Assignment Brief"
            actions={
              <div className="app-inline-group">
                <Link
                  to="/assignments"
                  search={{ course: selectedCourseId }}
                  className="app-inline-control"
                >
                  Back to List
                </Link>
              </div>
            }
          />

          <SurfacePanel muted className="app-editor-block app-form-stack">
            <FormFieldScaffold label="Title">
              <input
                className="app-form-input"
                value={formState.title}
                onChange={(event) =>
                  setFormState((current) => ({
                    ...current,
                    title: event.target.value,
                  }))
                }
                placeholder="Homework 4: Linked Lists"
              />
            </FormFieldScaffold>

            <FormFieldScaffold label="Description" support="Markdown-friendly prompt text">
              <textarea
                className="app-form-textarea"
                value={formState.description}
                onChange={(event) =>
                  setFormState((current) => ({
                    ...current,
                    description: event.target.value,
                  }))
                }
                placeholder="Describe the assignment requirements, starter assumptions, and expected output."
              />
            </FormFieldScaffold>
          </SurfacePanel>

          <SurfacePanel muted className="app-editor-callout">
            <strong>Course-linked editor</strong>
            <p>
              This editor now saves directly against the selected managed course.
              File attachments, version snapshots, and richer publishing controls can
              layer in later without changing the route or course-selection model.
            </p>
          </SurfacePanel>
        </div>

        <SurfacePanel muted className="app-editor-inspector">
          <SectionHeading title="Metadata" />
          <div className="app-inspector-grid">
            <FormFieldScaffold label="Course">
              <select
                className="app-form-input"
                value={selectedCourseId}
                onChange={(event) => handleCourseChange(event.target.value)}
                disabled={mode === "edit"}
              >
                {coursesQuery.data?.map((course) => (
                  <option key={course.id} value={course.id}>
                    {course.courseCode} • {course.title}
                  </option>
                ))}
              </select>
            </FormFieldScaffold>

            <FormFieldScaffold label="Assignment Type">
              <select
                className="app-form-input"
                value={formState.assignmentType}
                onChange={(event) =>
                  setFormState((current) => ({
                    ...current,
                    assignmentType: event.target.value as AssignmentType,
                  }))
                }
              >
                <option value="coding">Coding</option>
                <option value="document">Document</option>
                <option value="quiz">Quiz</option>
              </select>
            </FormFieldScaffold>

            <FormFieldScaffold label="Publish State">
              <select
                className="app-form-input"
                value={formState.publishState}
                onChange={(event) =>
                  setFormState((current) => ({
                    ...current,
                    publishState: event.target.value as AssignmentPublishState,
                  }))
                }
              >
                <option value="draft">Draft</option>
                <option value="published">Published</option>
                <option value="archived">Archived</option>
              </select>
            </FormFieldScaffold>
          </div>

          <div className="app-inspector-meta">
            <div className="app-meta-row">
              <span>Visibility</span>
              <StatusPill tone={formState.publishState === "published" ? "primary" : "default"}>
                {formState.publishState}
              </StatusPill>
            </div>
            <div className="app-meta-row">
              <span>Category</span>
              <StatusPill tone="primary">{formState.assignmentType}</StatusPill>
            </div>
          </div>

          <button className="app-verify-card" type="button">
            <Sparkles size={22} />
            Verify Environment
          </button>
        </SurfacePanel>
      </div>

      <BottomActionBar
        leading={
          <div className="app-status-cluster">
            <span className="app-smallcaps">Current Status</span>
            <strong>
              {assignmentMutation.isPending
                ? "Saving..."
                : mode === "edit"
                  ? "Editing existing assignment"
                  : "Create a new assignment"}
            </strong>
          </div>
        }
        actions={
          <>
            {assignmentMutation.isError ? (
              <span className="app-inline-error">
                {assignmentMutation.error instanceof Error
                  ? assignmentMutation.error.message
                  : "Could not save the assignment."}
              </span>
            ) : null}
            <button
              className="app-inline-action"
              type="button"
              onClick={() => submitWithState("draft")}
              disabled={assignmentMutation.isPending}
            >
              Save Draft
            </button>
            <button
              className="app-primary-action"
              type="button"
              onClick={() => submitWithState("published")}
              disabled={assignmentMutation.isPending}
            >
              {assignmentMutation.isPending ? "Saving..." : "Publish"}
            </button>
          </>
        }
      />
    </PageShell>
  );
}

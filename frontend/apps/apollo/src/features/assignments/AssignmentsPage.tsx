import { useEffect, useMemo } from "react";

import { useQuery } from "@tanstack/react-query";
import { Link, useNavigate } from "@tanstack/react-router";
import { BookOpen, CircleAlert, FilePlus2, LoaderCircle } from "lucide-react";
import { EmptyState, PageHeader, PageShell, SectionHeading, StatusPill, SurfacePanel } from "@optimark/calliope";

import {
  fetchCourseAssignments,
  fetchManagedCourses,
  managedAssignmentsQueryKey,
  managedCoursesQueryKey,
  sanitizeCourseId,
  type AssignmentPublishState,
  type ManagedCourse,
} from "./api";
import { assignmentsRoute } from "../../routes/assignments";

function formatAssignmentDate(value: string) {
  if (!value) {
    return "Recently updated";
  }

  const parsed = new Date(value);

  if (Number.isNaN(parsed.getTime())) {
    return "Recently updated";
  }

  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  }).format(parsed);
}

function assignmentTone(
  publishState: AssignmentPublishState,
): "default" | "primary" | "secondary" | "danger" {
  switch (publishState) {
    case "published":
      return "primary";
    case "archived":
      return "secondary";
    case "draft":
    default:
      return "default";
  }
}

function courseLabel(course: ManagedCourse) {
  return `${course.courseCode} • ${course.term}`;
}

export function AssignmentsPage() {
  const navigate = useNavigate({ from: assignmentsRoute.fullPath });
  const search = assignmentsRoute.useSearch();
  const {
    data: courses,
    isLoading: coursesLoading,
    isError: coursesError,
    error: coursesErrorValue,
  } = useQuery({
    queryKey: managedCoursesQueryKey,
    queryFn: fetchManagedCourses,
  });

  const selectedCourseId = useMemo(
    () => sanitizeCourseId(search.course) ?? courses?.[0]?.id,
    [courses, search.course],
  );
  const selectedCourse = courses?.find((course) => course.id === selectedCourseId) ?? null;

  useEffect(() => {
    if (selectedCourseId && selectedCourseId !== search.course) {
      void navigate({
        to: "/assignments",
        search: { course: selectedCourseId },
        replace: true,
      });
    }
  }, [navigate, search.course, selectedCourseId]);

  const assignmentsQuery = useQuery({
    queryKey: selectedCourseId
      ? managedAssignmentsQueryKey(selectedCourseId)
      : ["instructor", "courses", "unselected", "assignments"],
    queryFn: () => fetchCourseAssignments(selectedCourseId!),
    enabled: Boolean(selectedCourseId),
  });

  return (
    <PageShell>
      <PageHeader
        eyebrow="Instructor Management"
        title="Assignments"
        subtitle={
          selectedCourse
            ? `Manage coursework for ${selectedCourse.title} without leaving the protected workspace.`
            : "Select one of your managed courses to create and edit assignments."
        }
        actions={
          <Link
            to="/assignments/new"
            search={{ course: selectedCourseId }}
            className="app-primary-action"
          >
            <FilePlus2 size={16} />
            New Assignment
          </Link>
        }
      />

      <div className="app-management-grid">
        <SurfacePanel muted className="app-course-rail">
          <SectionHeading icon={<BookOpen size={16} />} title="Managed Courses" />

          {coursesLoading ? (
            <div className="app-panel-state">
              <LoaderCircle size={18} className="app-spin" />
              <span>Loading your course roster...</span>
            </div>
          ) : null}

          {coursesError ? (
            <div className="app-panel-state app-panel-state-error">
              <CircleAlert size={18} />
              <span>{coursesErrorValue instanceof Error ? coursesErrorValue.message : "Could not load courses."}</span>
            </div>
          ) : null}

          {!coursesLoading && !coursesError ? (
            <div className="app-course-stack">
              {courses?.map((course) => {
                const active = course.id === selectedCourseId;

                return (
                  <button
                    key={course.id}
                    type="button"
                    className={`app-course-card ${active ? "app-course-card-active" : ""}`.trim()}
                    onClick={() => {
                      void navigate({
                        to: "/assignments",
                        search: { course: course.id },
                      });
                    }}
                  >
                    <span className="app-smallcaps">{course.courseCode}</span>
                    <strong>{course.title}</strong>
                    <p>{course.term}</p>
                  </button>
                );
              })}
            </div>
          ) : null}
        </SurfacePanel>

        <SurfacePanel className="app-assignment-table-panel">
          <SectionHeading
            title={selectedCourse ? selectedCourse.title : "Course Assignments"}
            actions={selectedCourse ? <span className="app-smallcaps">{courseLabel(selectedCourse)}</span> : null}
          />

          {!selectedCourseId && !coursesLoading ? (
            <EmptyState
              icon={<BookOpen size={18} />}
              title="No managed courses yet"
              description="Once your instructor enrollments are available, course-specific assignment management will appear here."
            />
          ) : null}

          {assignmentsQuery.isLoading ? (
            <div className="app-panel-state">
              <LoaderCircle size={18} className="app-spin" />
              <span>Loading assignments...</span>
            </div>
          ) : null}

          {assignmentsQuery.isError ? (
            <div className="app-panel-state app-panel-state-error">
              <CircleAlert size={18} />
              <span>{assignmentsQuery.error instanceof Error ? assignmentsQuery.error.message : "Could not load assignments."}</span>
            </div>
          ) : null}

          {!assignmentsQuery.isLoading &&
          !assignmentsQuery.isError &&
          selectedCourse &&
          assignmentsQuery.data?.length ? (
            <table className="app-dense-table">
              <thead>
                <tr>
                  <th>Assignment</th>
                  <th>Type</th>
                  <th>Status</th>
                  <th>Updated</th>
                  <th className="align-right">Action</th>
                </tr>
              </thead>
              <tbody>
                {assignmentsQuery.data.map((assignment) => (
                  <tr key={assignment.id}>
                    <td>
                      <div className="app-assignment-cell">
                        <strong className="app-table-strong">{assignment.title}</strong>
                        <p>{assignment.description || "Add a clearer prompt in the editor."}</p>
                      </div>
                    </td>
                    <td>{assignment.assignmentType}</td>
                    <td>
                      <StatusPill tone={assignmentTone(assignment.publishState)}>
                        {assignment.publishState}
                      </StatusPill>
                    </td>
                    <td>{formatAssignmentDate(assignment.updatedAt)}</td>
                    <td className="align-right">
                      <Link
                        to="/courses/$courseId/assignments/$assignmentId"
                        params={{
                          assignmentId: assignment.id,
                          courseId: selectedCourse.id,
                        }}
                        className="app-inline-control"
                      >
                        Edit
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : null}

          {!assignmentsQuery.isLoading &&
          !assignmentsQuery.isError &&
          selectedCourse &&
          !assignmentsQuery.data?.length ? (
            <EmptyState
              icon={<FilePlus2 size={18} />}
              title="No assignments in this course yet"
              description="Create the first assignment for this course and we’ll keep the editor on the same managed-course context."
              action={
                <Link
                  to="/assignments/new"
                  search={{ course: selectedCourse.id }}
                  className="app-primary-action"
                >
                  Create First Assignment
                </Link>
              }
            />
          ) : null}
        </SurfacePanel>
      </div>
    </PageShell>
  );
}

import { createRoute } from "@tanstack/react-router";

import { sanitizeCourseId } from "../features/assignments/api";
import { AssignmentBuilderPage } from "../features/assignments/AssignmentBuilderPage";
import { protectedLayoutRoute } from "./protected";

function NewAssignmentRouteComponent() {
  const search = newAssignmentRoute.useSearch();
  return <AssignmentBuilderPage mode="create" courseId={search.course} />;
}

export const newAssignmentRoute = createRoute({
  getParentRoute: () => protectedLayoutRoute,
  path: "/assignments/new",
  validateSearch: (search) => ({
    course: sanitizeCourseId(search.course),
  }),
  component: NewAssignmentRouteComponent,
});

function EditAssignmentRouteComponent() {
  const { assignmentId } = editAssignmentRoute.useParams();
  const search = editAssignmentRoute.useSearch();
  return (
    <AssignmentBuilderPage
      mode="edit"
      assignmentId={assignmentId}
      courseId={search.course}
    />
  );
}

export const editAssignmentRoute = createRoute({
  getParentRoute: () => protectedLayoutRoute,
  path: "/assignments/$assignmentId",
  validateSearch: (search) => ({
    course: sanitizeCourseId(search.course),
  }),
  component: EditAssignmentRouteComponent,
});

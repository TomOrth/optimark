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
  const { assignmentId, courseId } = editAssignmentRoute.useParams();
  return (
    <AssignmentBuilderPage
      mode="edit"
      assignmentId={assignmentId}
      courseId={courseId}
    />
  );
}

export const editAssignmentRoute = createRoute({
  getParentRoute: () => protectedLayoutRoute,
  path: "/courses/$courseId/assignments/$assignmentId",
  component: EditAssignmentRouteComponent,
});

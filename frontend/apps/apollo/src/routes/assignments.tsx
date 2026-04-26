import { createRoute } from "@tanstack/react-router";

import { sanitizeCourseId } from "../features/assignments/api";
import { AssignmentsPage } from "../features/assignments/AssignmentsPage";
import { protectedLayoutRoute } from "./protected";

export const assignmentsRoute = createRoute({
  getParentRoute: () => protectedLayoutRoute,
  path: "/assignments",
  validateSearch: (search) => ({
    course: sanitizeCourseId(search.course),
  }),
  component: AssignmentsPage,
});

import { createRoute } from "@tanstack/react-router";

import { AssignmentsPage } from "../features/assignments/AssignmentsPage";
import { protectedLayoutRoute } from "./protected";

export const assignmentsRoute = createRoute({
  getParentRoute: () => protectedLayoutRoute,
  path: "/assignments",
  component: AssignmentsPage,
});

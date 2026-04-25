import { createRoute } from "@tanstack/react-router";

import { AssignmentBuilderPage } from "../features/assignments/AssignmentBuilderPage";
import { protectedLayoutRoute } from "./protected";

export const assignmentEditorRoute = createRoute({
  getParentRoute: () => protectedLayoutRoute,
  path: "/assignments/new",
  component: AssignmentBuilderPage,
});

import { createRoute } from "@tanstack/react-router";

import { SubmissionsPage } from "../features/submissions/SubmissionsPage";
import { protectedLayoutRoute } from "./protected";

export const submissionsRoute = createRoute({
  getParentRoute: () => protectedLayoutRoute,
  path: "/submissions",
  component: SubmissionsPage,
});

import { createRoute } from "@tanstack/react-router";

import { GradebookPage } from "../features/gradebook/GradebookPage";
import { protectedLayoutRoute } from "./protected";

export const gradebookRoute = createRoute({
  getParentRoute: () => protectedLayoutRoute,
  path: "/gradebook",
  component: GradebookPage,
});

import { createRoute } from "@tanstack/react-router";

import { StudentsPage } from "../features/students/StudentsPage";
import { protectedLayoutRoute } from "./protected";

export const studentsRoute = createRoute({
  getParentRoute: () => protectedLayoutRoute,
  path: "/students",
  component: StudentsPage,
});

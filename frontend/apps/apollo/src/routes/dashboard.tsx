import { createRoute } from "@tanstack/react-router";

import { DashboardPage } from "../features/dashboard/DashboardPage";
import { protectedLayoutRoute } from "./protected";

export const dashboardRoute = createRoute({
  getParentRoute: () => protectedLayoutRoute,
  path: "/dashboard",
  component: DashboardPage,
});

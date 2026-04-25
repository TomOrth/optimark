import { QueryClient } from "@tanstack/react-query";
import { createRoute, createRouter, redirect } from "@tanstack/react-router";

import { ensureSession } from "../features/auth/session";
import { assignmentEditorRoute } from "./assignment-editor";
import { assignmentsRoute } from "./assignments";
import { authLayoutRoute, loginRoute, signupRoute } from "./auth";
import { dashboardRoute } from "./dashboard";
import { gradebookRoute } from "./gradebook";
import { protectedLayoutRoute } from "./protected";
import { rootRoute, type AppContext } from "./root";
import { settingsRoute } from "./settings";
import { studentsRoute } from "./students";
import { submissionsRoute } from "./submissions";

export const queryClient = new QueryClient();

const indexRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/",
  beforeLoad: async ({ context }) => {
    const session = await ensureSession(context.queryClient);
    throw redirect({ to: session ? "/dashboard" : "/login" });
  },
});

const routeTree = rootRoute.addChildren([
  indexRoute,
  authLayoutRoute.addChildren([loginRoute, signupRoute]),
  protectedLayoutRoute.addChildren([
    dashboardRoute,
    assignmentsRoute,
    assignmentEditorRoute,
    submissionsRoute,
    gradebookRoute,
    studentsRoute,
    settingsRoute,
  ]),
]);

export const router = createRouter({
  routeTree,
  context: {
    queryClient,
  } satisfies AppContext,
  defaultPreload: "intent",
});

declare module "@tanstack/react-router" {
  interface Register {
    router: typeof router;
  }
}

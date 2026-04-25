import { createRoute } from "@tanstack/react-router";

import { requireAuthenticated } from "../features/auth/session";
import { ProtectedAppLayout } from "../features/shell/ProtectedAppLayout";
import { rootRoute } from "./root";

export const protectedLayoutRoute = createRoute({
  getParentRoute: () => rootRoute,
  id: "protected-layout",
  beforeLoad: async ({ context, location }) => {
    await requireAuthenticated(context.queryClient, location.pathname);
  },
  component: ProtectedAppLayout,
});

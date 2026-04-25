import type { QueryClient } from "@tanstack/react-query";
import { Outlet, createRootRouteWithContext } from "@tanstack/react-router";

export type AppContext = {
  queryClient: QueryClient;
};

function RootRouteComponent() {
  return <Outlet />;
}

export const rootRoute = createRootRouteWithContext<AppContext>()({
  component: RootRouteComponent,
});

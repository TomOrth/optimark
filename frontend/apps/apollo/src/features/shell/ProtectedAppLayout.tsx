import { Outlet } from "@tanstack/react-router";
import { AppFrame } from "@optimark/calliope";

import { AppSidebar } from "./AppSidebar";
import { AppTopbar } from "./AppTopbar";

export function ProtectedAppLayout() {
  return (
    <AppFrame sidebar={<AppSidebar />} topbar={<AppTopbar />}>
      <Outlet />
    </AppFrame>
  );
}

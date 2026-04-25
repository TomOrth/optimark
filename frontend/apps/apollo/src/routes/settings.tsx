import { createRoute } from "@tanstack/react-router";

import { SettingsPage } from "../features/settings/SettingsPage";
import { protectedLayoutRoute } from "./protected";

export const settingsRoute = createRoute({
  getParentRoute: () => protectedLayoutRoute,
  path: "/settings",
  component: SettingsPage,
});

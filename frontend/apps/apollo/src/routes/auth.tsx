import { createRoute } from "@tanstack/react-router";

import { LoginPage } from "../features/auth/routes/LoginPage";
import { SignupPage } from "../features/auth/routes/SignupPage";
import {
  redirectAuthenticated,
  sanitizeRedirectPath,
  type AuthSearch,
} from "../features/auth/session";
import { AuthLayout } from "../features/shell/AuthLayout";
import { rootRoute } from "./root";

export const authLayoutRoute = createRoute({
  getParentRoute: () => rootRoute,
  id: "auth-layout",
  component: AuthLayout,
});

export const loginRoute = createRoute({
  getParentRoute: () => authLayoutRoute,
  path: "/login",
  validateSearch: (search: Record<string, unknown>): AuthSearch => ({
    redirect: sanitizeRedirectPath(search.redirect),
  }),
  beforeLoad: async ({ context, search }) => {
    await redirectAuthenticated(context.queryClient, sanitizeRedirectPath(search.redirect));
  },
  component: LoginPage,
});

export const signupRoute = createRoute({
  getParentRoute: () => authLayoutRoute,
  path: "/signup",
  validateSearch: (search: Record<string, unknown>): AuthSearch => ({
    redirect: sanitizeRedirectPath(search.redirect),
  }),
  beforeLoad: async ({ context, search }) => {
    await redirectAuthenticated(context.queryClient, sanitizeRedirectPath(search.redirect));
  },
  component: SignupPage,
});

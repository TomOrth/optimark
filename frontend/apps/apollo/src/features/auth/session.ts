import type { QueryClient } from "@tanstack/react-query";
import { redirect } from "@tanstack/react-router";

import { ApiError } from "../../lib/api/client";
import { apiClient, type SessionResponse } from "../../lib/api/generated";

export type AuthSearch = {
  redirect?: string;
};

type RedirectLocation = {
  pathname: string;
  searchStr?: string;
  hash?: string;
};

export const sessionQueryKey = ["auth", "session"] as const;

export async function fetchSession(): Promise<SessionResponse | null> {
  try {
    return await apiClient.getSession();
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) {
      return null;
    }

    throw error;
  }
}

export function sessionQueryOptions() {
  return {
    queryKey: sessionQueryKey,
    queryFn: fetchSession,
    staleTime: 60_000,
    retry: false,
  };
}

export function sanitizeRedirectPath(value: unknown): string | undefined {
  if (typeof value !== "string") {
    return undefined;
  }

  const trimmed = value.trim();

  if (!trimmed) {
    return undefined;
  }

  let decodedValue = trimmed;

  try {
    decodedValue = decodeURIComponent(trimmed);
  } catch {
    return undefined;
  }

  if (/[\u0000-\u001F\u007F]/.test(decodedValue)) {
    return undefined;
  }

  if (!decodedValue.startsWith("/") || decodedValue.startsWith("//")) {
    return undefined;
  }

  const firstNestedSlash = decodedValue.indexOf("/", 1);
  const leadingSegment =
    firstNestedSlash === -1 ? decodedValue.slice(1) : decodedValue.slice(1, firstNestedSlash);

  if (leadingSegment.includes(":") || decodedValue.includes("://")) {
    return undefined;
  }

  return decodedValue;
}

export function deriveInitials(displayName: string): string {
  return displayName
    .trim()
    .split(/\s+/)
    .filter(Boolean)
    .map((part) => part[0] ?? "")
    .join("")
    .slice(0, 2)
    .toUpperCase();
}

export function buildRedirectPath(location: RedirectLocation): string {
  return `${location.pathname}${location.searchStr ?? ""}${location.hash ?? ""}`;
}

export async function ensureSession(queryClient: QueryClient): Promise<SessionResponse | null> {
  return queryClient.ensureQueryData(sessionQueryOptions());
}

export async function requireAuthenticated(queryClient: QueryClient, redirectPath: string) {
  const session = await ensureSession(queryClient);

  if (!session) {
    throw redirect({
      to: "/login",
      search: { redirect: redirectPath },
    });
  }

  return session;
}

export async function redirectAuthenticated(
  queryClient: QueryClient,
  redirectPath?: string,
) {
  const session = await ensureSession(queryClient);

  if (session) {
    throw redirect({ to: redirectPath || "/dashboard" });
  }
}

import { ApiError, requestJson } from "../../lib/api/client";
import type { SessionResponse } from "./session";

export type AuthPayload = {
  email: string;
  password: string;
};

export type SignupPayload = AuthPayload & {
  display_name: string;
};

export async function loginRequest(payload: AuthPayload): Promise<SessionResponse> {
  return requestJson<SessionResponse>("/api/v1/auth/login", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function signupRequest(payload: SignupPayload): Promise<SessionResponse> {
  return requestJson<SessionResponse>("/api/v1/auth/signup", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function logoutRequest(): Promise<void> {
  const response = await fetch("/api/v1/auth/logout", {
    method: "POST",
    credentials: "include",
  });

  if (response.ok || response.status === 401) {
    return;
  }

  if (!response.ok) {
    throw new ApiError(response.status, "Unable to end the current session.");
  }
}

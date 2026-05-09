import { ApiError } from "../../lib/api/client";
import {
  apiClient,
  type LoginRequest,
  type SessionResponse,
  type SignupRequest,
} from "../../lib/api/generated";

export type AuthPayload = LoginRequest;
export type SignupPayload = SignupRequest;

export async function loginRequest(payload: AuthPayload): Promise<SessionResponse> {
  return apiClient.login(payload);
}

export async function signupRequest(payload: SignupPayload): Promise<SessionResponse> {
  return apiClient.signup(payload);
}

export async function logoutRequest(): Promise<void> {
  return apiClient.logout();
}

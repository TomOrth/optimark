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
  try {
    await apiClient.logout();
  } catch (error) {
      if (error instanceof ApiError && error.status === 401) {
        return;
      }
  
      if (error instanceof ApiError) {
        throw new ApiError(error.status, "Unable to end the current session.");
      }
  
    if (response.ok || response.status === 401) {
      return;
    }
  
    if (!response.ok) {
      throw new ApiError(response.status, "Unable to end the current session.");
    }
  }
}

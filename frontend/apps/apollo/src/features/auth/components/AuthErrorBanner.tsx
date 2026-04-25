import { CircleAlert } from "lucide-react";

import { ApiError } from "../../../lib/api/client";

export function AuthErrorBanner({ error }: { error: unknown }) {
  const detail =
    error instanceof ApiError
      ? error.message
      : "Something went wrong. Please try again.";

  return (
    <div className="app-auth-error" role="alert">
      <CircleAlert size={16} />
      <span>{detail}</span>
    </div>
  );
}

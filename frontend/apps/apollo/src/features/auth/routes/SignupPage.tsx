import { useState } from "react";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Link, useNavigate, useRouterState } from "@tanstack/react-router";
import { LoaderCircle } from "lucide-react";
import { FormFieldScaffold } from "@optimark/calliope";

import { signupRequest } from "../api";
import {
  sessionQueryKey,
  type AuthSearch,
} from "../session";
import { AuthCard } from "../components/AuthCard";
import { AuthErrorBanner } from "../components/AuthErrorBanner";

export function SignupPage() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const search = useRouterState({
    select: (state) => (state.location.search as AuthSearch) ?? {},
  });
  const [displayName, setDisplayName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const signup = useMutation({
    mutationFn: signupRequest,
    onSuccess: async (session) => {
      queryClient.setQueryData(sessionQueryKey, session);
      await navigate({ to: search.redirect || "/dashboard" });
    },
  });

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    signup.mutate({ display_name: displayName, email, password });
  }

  return (
    <AuthCard
      eyebrow="Create Account"
      title="Open a new course session."
      subtitle="This initial hosted flow stays intentionally simple while preserving the backend seam for future SSO."
      footer={
        <p className="app-auth-footer">
          Already have access?{" "}
          <Link to="/login" search={{ redirect: search.redirect }}>
            Sign in
          </Link>
        </p>
      }
    >
      <form className="app-auth-form" onSubmit={onSubmit}>
        <FormFieldScaffold label="Display Name">
          <input
            className="app-auth-input"
            type="text"
            autoComplete="name"
            value={displayName}
            onChange={(event) => setDisplayName(event.target.value)}
            placeholder="Dr. Aris Thorne"
            required
          />
        </FormFieldScaffold>
        <FormFieldScaffold label="Email Address">
          <input
            className="app-auth-input"
            type="email"
            autoComplete="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            placeholder="instructor@university.edu"
            required
          />
        </FormFieldScaffold>
        <FormFieldScaffold label="Password" support="Minimum 12 characters.">
          <input
            className="app-auth-input"
            type="password"
            autoComplete="new-password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            placeholder="Choose a strong password"
            required
          />
        </FormFieldScaffold>
        {signup.isError ? <AuthErrorBanner error={signup.error} /> : null}
        <button
          className="app-primary-action app-auth-submit"
          type="submit"
          disabled={signup.isPending}
        >
          {signup.isPending ? <LoaderCircle size={16} className="app-spin" /> : null}
          Create Account
        </button>
      </form>
    </AuthCard>
  );
}

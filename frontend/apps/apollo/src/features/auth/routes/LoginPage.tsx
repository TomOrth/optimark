import { useState } from "react";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Link, useNavigate, useRouterState } from "@tanstack/react-router";
import { LoaderCircle } from "lucide-react";
import { FormFieldScaffold } from "@optimark/calliope";

import { loginRequest } from "../api";
import {
  sessionQueryKey,
  type AuthSearch,
} from "../session";
import { AuthCard } from "../components/AuthCard";
import { AuthErrorBanner } from "../components/AuthErrorBanner";

export function LoginPage() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const search = useRouterState({
    select: (state) => (state.location.search as AuthSearch) ?? {},
  });
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const login = useMutation({
    mutationFn: loginRequest,
    onSuccess: async (session) => {
      queryClient.setQueryData(sessionQueryKey, session);
      await navigate({ to: search.redirect || "/dashboard" });
    },
  });

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    login.mutate({ email, password });
  }

  return (
    <AuthCard
      eyebrow="Sign In"
      title="Resume your hosted workspace."
      subtitle="Use the account created through the backend auth foundation to restore your session."
      footer={
        <p className="app-auth-footer">
          Need an account?{" "}
          <Link to="/signup" search={{ redirect: search.redirect }}>
            Create one
          </Link>
        </p>
      }
    >
      <form className="app-auth-form" onSubmit={onSubmit}>
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
        <FormFieldScaffold label="Password">
          <input
            className="app-auth-input"
            type="password"
            autoComplete="current-password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            placeholder="At least 12 characters"
            required
          />
        </FormFieldScaffold>
        {login.isError ? <AuthErrorBanner error={login.error} /> : null}
        <button
          className="app-primary-action app-auth-submit"
          type="submit"
          disabled={login.isPending}
        >
          {login.isPending ? <LoaderCircle size={16} className="app-spin" /> : null}
          Sign In
        </button>
      </form>
    </AuthCard>
  );
}

import { useMemo } from "react";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useNavigate } from "@tanstack/react-router";
import { Code2, LayoutDashboard, BookOpen, ListChecks, ChartColumn, Users, Settings, LoaderCircle, LogOut } from "lucide-react";
import {
  BrandLockup,
  SidebarNavItem,
  SidebarShell,
  brand,
  sidebarUtilityLinks,
} from "@optimark/calliope";

import { logoutRequest } from "../auth/api";
import { deriveInitials, sessionQueryKey, sessionQueryOptions } from "../auth/session";

const navItems = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/assignments", label: "Assignments", icon: BookOpen },
  { to: "/submissions", label: "Submissions", icon: ListChecks },
  { to: "/gradebook", label: "Gradebook", icon: ChartColumn },
  { to: "/students", label: "Students", icon: Users },
  { to: "/settings", label: "Settings", icon: Settings },
] as const;

function SidebarProfile({
  displayName,
  email,
}: {
  displayName: string;
  email: string;
}) {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const logout = useMutation({
    mutationFn: logoutRequest,
    onSuccess: async () => {
      queryClient.setQueryData(sessionQueryKey, null);
      await navigate({ to: "/login" });
    },
  });
  const initials = useMemo(() => deriveInitials(displayName), [displayName]);

  return (
    <div className="app-profile-stack">
      <div className="app-profile-chip">
        <div className="app-profile-avatar">{initials}</div>
        <div>
          <strong>{displayName}</strong>
          <p>{email}</p>
        </div>
      </div>
      <button
        className="app-secondary-action app-sidebar-logout"
        type="button"
        onClick={() => logout.mutate()}
        disabled={logout.isPending}
      >
        {logout.isPending ? <LoaderCircle size={16} className="app-spin" /> : <LogOut size={16} />}
        Log Out
      </button>
      {logout.isError ? (
        <p className="app-inline-error">We could not end the current session. Try again.</p>
      ) : null}
    </div>
  );
}

export function AppSidebar() {
  const { data: session } = useQuery(sessionQueryOptions());

  return (
    <SidebarShell
      brand={
        <BrandLockup
          name={brand.name}
          context={brand.courseLabel}
          mark={<Code2 size={18} />}
        />
      }
      navigation={navItems.map(({ to, label, icon: Icon }) =>
        to === "/assignments" ? (
          <Link key={to} to={to} search={{ course: undefined }}>
            {({ isActive }) => (
              <SidebarNavItem active={isActive} icon={<Icon size={20} />} label={label} />
            )}
          </Link>
        ) : (
          <Link key={to} to={to}>
            {({ isActive }) => (
              <SidebarNavItem active={isActive} icon={<Icon size={20} />} label={label} />
            )}
          </Link>
        ),
      )}
      primaryAction={
        <Link to="/assignments/new" search={{ course: undefined }} className="app-primary-action">
          New Assessment
        </Link>
      }
      utilityLinks={sidebarUtilityLinks.map((item) => (
        <div key={item.key} className="app-utility-link">
          {item.label}
        </div>
      ))}
      profile={
        <SidebarProfile
          displayName={session?.user.display_name ?? brand.instructorName}
          email={session?.user.email ?? "staff@optimark.dev"}
        />
      }
    />
  );
}

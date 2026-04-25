import { useMemo } from "react";

import { useQuery } from "@tanstack/react-query";
import { useRouterState } from "@tanstack/react-router";
import { Bell, History, Search } from "lucide-react";
import { Topbar, TopbarTab, brand, topTabs } from "@optimark/calliope";

import { deriveInitials, sessionQueryOptions } from "../auth/session";

export function AppTopbar() {
  const pathname = useRouterState({
    select: (state) => state.location.pathname,
  });
  const { data: session } = useQuery(sessionQueryOptions());
  const activeTopTab = pathname === "/gradebook" ? "analytics" : "course-settings";
  const initials = useMemo(
    () => deriveInitials(session?.user.display_name ?? brand.instructorName),
    [session?.user.display_name],
  );

  return (
    <Topbar
      tabs={topTabs.map((tab) => (
        <TopbarTab key={tab.key} active={tab.key === activeTopTab}>
          {tab.label}
        </TopbarTab>
      ))}
      search={
        <label className="app-search">
          <Search size={16} />
          <input placeholder="Search assessments..." />
        </label>
      }
      tools={
        <div className="app-topbar-tools">
          <button className="app-icon-button" type="button" aria-label="Notifications">
            <Bell size={18} />
          </button>
          <button className="app-icon-button" type="button" aria-label="History">
            <History size={18} />
          </button>
          <div className="app-topbar-session">
            <span>{session?.user.display_name ?? brand.instructorName}</span>
            <div className="app-topbar-avatar">{initials}</div>
          </div>
        </div>
      }
    />
  );
}

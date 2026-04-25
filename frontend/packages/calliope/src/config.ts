/** Shared Calliope configuration and design-token values. */

export const brand = {
  name: "Optimark",
  courseLabel: "CS101: Data Structures",
  courseTerm: "Fall 2026 Term",
  viewLabel: "Instructor View",
  instructorName: "Dr. Aris Thorne",
  instructorRole: "Lead Instructor",
} as const;

export const topTabs = [
  { key: "course-settings", label: "Course Settings" },
  { key: "analytics", label: "Analytics" },
  { key: "audit-log", label: "Audit Log" },
] as const;

export const sidebarUtilityLinks = [
  { key: "help", label: "Help" },
  { key: "archive", label: "Archive" },
] as const;

export const designTokens = {
  color: {
    background: "#f9f9f8",
    surface: "#ffffff",
    surfaceLow: "#f1f4f3",
    surfaceContainer: "#eaefee",
    surfaceHigh: "#e3e9e8",
    surfaceHighest: "#dce4e3",
    surfaceDim: "#d2dcdb",
    outlineVariant: "#abb4b3",
    text: "#2c3433",
    textMuted: "#586160",
    primary: "#306576",
    primaryDim: "#215969",
    primaryContainer: "#b6ebfe",
    secondaryContainer: "#d5e3fc",
    error: "#9f403d",
    errorContainer: "#fe8983",
  },
  radius: {
    sm: "0.25rem",
    md: "0.5rem",
    lg: "0.75rem",
    xl: "1.25rem",
  },
  shadow: {
    ambient: "0 12px 40px rgba(44, 52, 51, 0.06)",
    subtle: "0 10px 28px rgba(44, 52, 51, 0.04)",
  },
  type: {
    displayFamily: "Manrope, sans-serif",
    bodyFamily: "Inter, sans-serif",
  },
} as const;

import { CircleAlert, FileCode2, SquareTerminal } from "lucide-react";

export const assignmentRows = [
  {
    name: "Homework 4: Linked Lists",
    type: "Practical",
    status: { label: "Published", tone: "primary" as const },
    due: "Oct 12, 23:59",
    submissions: "42 / 45",
  },
  {
    name: "Assignment 3: Binary Trees",
    type: "Programming",
    status: { label: "Reviewing", tone: "secondary" as const },
    due: "Oct 05, 12:00",
    submissions: "45 / 45",
  },
  {
    name: "Midterm Quiz: Core Concepts",
    type: "Exam",
    status: { label: "Draft", tone: "default" as const },
    due: "Oct 24, 09:00",
    submissions: "0 / 45",
  },
  {
    name: "Homework 5: Graph Theory",
    type: "Practical",
    status: { label: "Draft", tone: "default" as const },
    due: "Nov 02, 23:59",
    submissions: "0 / 45",
  },
] as const;

export const activityFeed = [
  {
    title: "Student A submitted Homework 4",
    when: "12 minutes ago",
    detail: "New programming artifact is ready for queueing.",
    tone: "primary" as const,
    icon: <FileCode2 size={16} />,
  },
  {
    title: "Autograde completed for Assignment 3",
    when: "45 minutes ago",
    detail: "82% average • 4 error flags surfaced for review.",
    tone: "secondary" as const,
    icon: <FileCode2 size={16} />,
  },
  {
    title: "Manual review started on Midterm Essays",
    when: "2 hours ago",
    detail: "TA review batch is currently in progress.",
    tone: "default" as const,
    icon: <SquareTerminal size={16} />,
  },
  {
    title: "System: Plagiarism detected in Homework 4",
    when: "3 hours ago",
    detail: "One critical alert needs instructor verification.",
    tone: "danger" as const,
    icon: <CircleAlert size={16} />,
  },
] as const;

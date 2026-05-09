import { createRoute } from "@tanstack/react-router";

import { SubmissionWorkspacePage } from "../features/submissions/SubmissionWorkspacePage";
import { protectedLayoutRoute } from "./protected";

export const submissionWorkspaceRoute = createRoute({
  getParentRoute: () => protectedLayoutRoute,
  path: "/submissions/$courseId/$assignmentId",
  component: SubmissionWorkspaceRouteComponent,
});

function SubmissionWorkspaceRouteComponent() {
  const { assignmentId, courseId } = submissionWorkspaceRoute.useParams();
  return <SubmissionWorkspacePage assignmentId={assignmentId} courseId={courseId} />;
}

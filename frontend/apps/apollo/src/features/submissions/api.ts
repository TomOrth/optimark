import { request, requestJson } from "../../lib/api/client";

export type SubmissionLifecycleStatus =
  | "draft"
  | "submitted"
  | "queued"
  | "running"
  | "completed"
  | "failed"
  | "withdrawn";

export type CourseSummary = {
  id: string;
  course_code: string;
  title: string;
  term: string;
};

export type AssignmentDetail = {
  id: string;
  course_id: string;
  title: string;
  description: string;
  assignment_type: string;
  publish_state: string;
  created_at: string;
  updated_at: string;
};

export type StudentSubmissionRecord = {
  id: string;
  assignment_id: string;
  assignment_version_id: string;
  student_user_id: string;
  state: string;
  lifecycle_status: SubmissionLifecycleStatus;
  artifact_key: string | null;
  artifact_name: string | null;
  submitted_at: string | null;
  created_at: string;
  updated_at: string;
};

export type StudentAssignmentSummary = {
  course: CourseSummary;
  assignment: AssignmentDetail;
  active_assignment_version_id: string | null;
  latest_submission: StudentSubmissionRecord | null;
};

export type StudentSubmissionWorkspace = {
  course: CourseSummary;
  assignment: AssignmentDetail;
  active_assignment_version_id: string | null;
  submissions: StudentSubmissionRecord[];
};

export type CreateSubmissionInput = {
  courseId: string;
  assignmentId: string;
  file: File;
  state: "draft" | "submitted";
};

export async function fetchStudentAssignments(): Promise<StudentAssignmentSummary[]> {
  return requestJson<StudentAssignmentSummary[]>("/api/v1/student/assignments", {
    method: "GET",
  });
}

export async function fetchSubmissionWorkspace(
  courseId: string,
  assignmentId: string,
): Promise<StudentSubmissionWorkspace> {
  return requestJson<StudentSubmissionWorkspace>(
    `/api/v1/courses/${courseId}/assignments/${assignmentId}/submission-workspace`,
    {
      method: "GET",
    },
  );
}

export async function createSubmission({
  courseId,
  assignmentId,
  file,
  state,
}: CreateSubmissionInput): Promise<StudentSubmissionRecord> {
  const query = new URLSearchParams({
    filename: file.name,
    state,
  });
  const response = await request(
    `/api/v1/courses/${courseId}/assignments/${assignmentId}/submissions?${query.toString()}`,
    {
      method: "POST",
      body: file,
      headers: {
        "Content-Type": file.type || "application/octet-stream",
      },
    },
  );

  return (await response.json()) as StudentSubmissionRecord;
}

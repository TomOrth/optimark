import {
  apiClient,
  type AssignmentDetail,
  type AssignmentPublishState,
  type AssignmentSummary,
  type AssignmentType,
  type CourseSummary,
  type CreateCourseAssignmentInput,
  type UpdateAssignmentInput,
} from "../../lib/api/generated";

export type ManagedCourse = {
  id: string;
  courseCode: string;
  title: string;
  term: string;
};

export type ManagedAssignment = {
  id: string;
  courseId: string;
  title: string;
  description: string;
  assignmentType: AssignmentType;
  publishState: AssignmentPublishState;
  createdAt: string;
  updatedAt: string;
};

export type { AssignmentPublishState, AssignmentType };

export type AssignmentWritePayload = {
  title: string;
  description: string;
  assignmentType: AssignmentType;
  publishState: AssignmentPublishState;
};

export const managedCoursesQueryKey = ["instructor", "courses"] as const;

export function managedAssignmentsQueryKey(courseId: string) {
  return ["instructor", "courses", courseId, "assignments"] as const;
}

export function assignmentDetailQueryKey(courseId: string, assignmentId: string) {
  return ["instructor", "courses", courseId, "assignments", assignmentId] as const;
}

function normalizeCourse(course: CourseSummary): ManagedCourse {
  return {
    id: course.id,
    courseCode: course.course_code,
    title: course.title,
    term: course.term,
  };
}

function normalizeAssignment(
  assignment: AssignmentSummary | AssignmentDetail,
): ManagedAssignment {
  return {
    id: assignment.id,
    courseId: assignment.course_id,
    title: assignment.title,
    description: "description" in assignment ? assignment.description : "",
    assignmentType: assignment.assignment_type,
    publishState: assignment.publish_state,
    createdAt: "created_at" in assignment ? assignment.created_at : "",
    updatedAt: "updated_at" in assignment ? assignment.updated_at : "",
  };
}

function toCreateAssignmentInput(
  payload: AssignmentWritePayload,
): CreateCourseAssignmentInput {
  return {
    title: payload.title,
    description: payload.description,
    assignment_type: payload.assignmentType,
    publish_state: payload.publishState,
  };
}

function toUpdateAssignmentInput(payload: AssignmentWritePayload): UpdateAssignmentInput {
  return {
    title: payload.title,
    description: payload.description,
    assignment_type: payload.assignmentType,
    publish_state: payload.publishState,
  };
}

export function sanitizeCourseId(value: unknown): string | undefined {
  if (typeof value !== "string") {
    return undefined;
  }

  const trimmed = value.trim();

  if (!trimmed) {
    return undefined;
  }

  return /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(trimmed)
    ? trimmed
    : undefined;
}

export async function fetchManagedCourses(): Promise<ManagedCourse[]> {
  const courses = await apiClient.listManagedCourses();
  return courses.map(normalizeCourse);
}

export async function fetchCourseAssignments(courseId: string): Promise<ManagedAssignment[]> {
  const assignments = await apiClient.listCourseAssignments({ course_id: courseId });
  return assignments.map(normalizeAssignment);
}

export async function fetchAssignmentDetail(
  courseId: string,
  assignmentId: string,
): Promise<ManagedAssignment> {
  const assignment = await apiClient.getCourseAssignment({
    course_id: courseId,
    assignment_id: assignmentId,
  });
  return normalizeAssignment(assignment);
}

export async function createAssignment(
  courseId: string,
  payload: AssignmentWritePayload,
): Promise<ManagedAssignment> {
  const assignment = await apiClient.createCourseAssignment(
    { course_id: courseId },
    toCreateAssignmentInput(payload),
  );
  return normalizeAssignment(assignment);
}

export async function updateAssignment(
  courseId: string,
  assignmentId: string,
  payload: AssignmentWritePayload,
): Promise<ManagedAssignment> {
  const assignment = await apiClient.updateCourseAssignment(
    { course_id: courseId, assignment_id: assignmentId },
    toUpdateAssignmentInput(payload),
  );
  return normalizeAssignment(assignment);
}

import { requestJson } from "../../lib/api/client";

export type ManagedCourse = {
  id: string;
  courseCode: string;
  title: string;
  term: string;
};

export type AssignmentType = "coding" | "document" | "quiz";

export type AssignmentPublishState = "draft" | "published" | "archived";

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

export type AssignmentWritePayload = {
  title: string;
  description: string;
  assignmentType: AssignmentType;
  publishState: AssignmentPublishState;
};

type RawManagedCourse = {
  id: string;
  course_code?: string;
  courseCode?: string;
  title: string;
  term: string;
};

type RawManagedAssignment = {
  id: string;
  course_id?: string;
  courseId?: string;
  title: string;
  description: string;
  assignment_type?: AssignmentType;
  assignmentType?: AssignmentType;
  publish_state?: AssignmentPublishState;
  publishState?: AssignmentPublishState;
  created_at?: string;
  createdAt?: string;
  updated_at?: string;
  updatedAt?: string;
};

export const managedCoursesQueryKey = ["instructor", "courses"] as const;

export function managedAssignmentsQueryKey(courseId: string) {
  return ["instructor", "courses", courseId, "assignments"] as const;
}

export function assignmentDetailQueryKey(courseId: string, assignmentId: string) {
  return ["instructor", "courses", courseId, "assignments", assignmentId] as const;
}

function normalizeCourse(course: RawManagedCourse): ManagedCourse {
  return {
    id: course.id,
    courseCode: course.courseCode ?? course.course_code ?? "Course",
    title: course.title,
    term: course.term,
  };
}

function normalizeAssignment(assignment: RawManagedAssignment): ManagedAssignment {
  return {
    id: assignment.id,
    courseId: assignment.courseId ?? assignment.course_id ?? "",
    title: assignment.title,
    description: assignment.description,
    assignmentType: assignment.assignmentType ?? assignment.assignment_type ?? "coding",
    publishState: assignment.publishState ?? assignment.publish_state ?? "draft",
    createdAt: assignment.createdAt ?? assignment.created_at ?? "",
    updatedAt: assignment.updatedAt ?? assignment.updated_at ?? "",
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
  const courses = await requestJson<RawManagedCourse[]>("/api/v1/courses/managed", {
    method: "GET",
  });

  return courses.map(normalizeCourse);
}

export async function fetchCourseAssignments(courseId: string): Promise<ManagedAssignment[]> {
  const assignments = await requestJson<RawManagedAssignment[]>(
    `/api/v1/courses/${courseId}/assignments`,
    {
      method: "GET",
    },
  );

  return assignments.map(normalizeAssignment);
}

export async function fetchAssignmentDetail(
  courseId: string,
  assignmentId: string,
): Promise<ManagedAssignment> {
  const assignment = await requestJson<RawManagedAssignment>(
    `/api/v1/courses/${courseId}/assignments/${assignmentId}`,
    {
      method: "GET",
    },
  );

  return normalizeAssignment(assignment);
}

export async function createAssignment(
  courseId: string,
  payload: AssignmentWritePayload,
): Promise<ManagedAssignment> {
  const assignment = await requestJson<RawManagedAssignment>(
    `/api/v1/courses/${courseId}/assignments`,
    {
      method: "POST",
      body: JSON.stringify({
        title: payload.title,
        description: payload.description,
        assignment_type: payload.assignmentType,
        publish_state: payload.publishState,
      }),
    },
  );

  return normalizeAssignment(assignment);
}

export async function updateAssignment(
  courseId: string,
  assignmentId: string,
  payload: AssignmentWritePayload,
): Promise<ManagedAssignment> {
  const assignment = await requestJson<RawManagedAssignment>(
    `/api/v1/courses/${courseId}/assignments/${assignmentId}`,
    {
      method: "PATCH",
      body: JSON.stringify({
        title: payload.title,
        description: payload.description,
        assignment_type: payload.assignmentType,
        publish_state: payload.publishState,
      }),
    },
  );

  return normalizeAssignment(assignment);
}

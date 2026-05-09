export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

export async function request(path: string, init?: RequestInit): Promise<Response> {
  const response = await fetch(path, {
    ...init,
    credentials: "include",
    headers: {
      ...(init?.headers ?? {}),
    },
  });

  if (!response.ok) {
    throw new ApiError(response.status, await readErrorDetail(response));
  }

  return response;
}

export async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await request(path, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
  });

  return (await response.json()) as T;
}

export async function requestVoid(path: string, init?: RequestInit): Promise<void> {
  await request(path, init);
}

async function readErrorDetail(response: Response): Promise<string> {
  let detail = "Request failed.";

  try {
    const body = (await response.json()) as { detail?: string };
    detail = body.detail ?? detail;
  } catch {
    detail = response.statusText || detail;
  }

  return detail;
}

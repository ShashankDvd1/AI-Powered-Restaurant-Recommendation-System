const API_URL =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ||
  "http://localhost:8000";

export interface HealthResponse {
  status: string;
  data_ready: boolean;
  data_path: string;
  restaurant_count: number | null;
}

export async function fetchHealth(): Promise<HealthResponse> {
  const res = await fetch(`${API_URL}/health`, {
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`Health check failed: ${res.status} ${res.statusText}`);
  }
  return res.json() as Promise<HealthResponse>;
}

export function getApiUrl(): string {
  return API_URL;
}

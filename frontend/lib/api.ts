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

export interface RecommendationRequest {
  location: string;
  budget: "low" | "medium" | "high";
  cuisine: string;
  min_rating: number;
  extra_preferences?: string;
  top_k?: number;
}

export interface RecommendationItem {
  restaurant_name: string;
  cuisine: string;
  rating: number;
  estimated_cost: string;
  explanation: string;
}

export interface RecommendationMeta {
  candidate_count: number;
  source: "grok" | "fallback";
}

export interface RecommendationResponse {
  summary: string;
  recommendations: RecommendationItem[];
  meta: RecommendationMeta;
}

export async function getRecommendations(
  preferences: RecommendationRequest
): Promise<RecommendationResponse> {
  const res = await fetch(`${API_URL}/recommendations`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(preferences),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    const message = errorData.detail || `Server error: ${res.status} ${res.statusText}`;
    const err = new Error(message);
    (err as any).status = res.status;
    (err as any).detail = errorData.detail;
    throw err;
  }
  return res.json() as Promise<RecommendationResponse>;
}

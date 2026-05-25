"use client";

import { useEffect, useState } from "react";
import { fetchHealth, getApiUrl, type HealthResponse } from "@/lib/api";

type Status = "loading" | "ok" | "error";

export default function HealthStatus() {
  const [status, setStatus] = useState<Status>("loading");
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const data = await fetchHealth();
        if (!cancelled) {
          setHealth(data);
          setStatus("ok");
          setError(null);
        }
      } catch (e) {
        if (!cancelled) {
          setStatus("error");
          setError(e instanceof Error ? e.message : "Unknown error");
        }
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <section className="health-card">
      <h2>Backend status</h2>
      <p className="muted">
        API: <code>{getApiUrl()}</code>
      </p>

      {status === "loading" && <p>Checking /health…</p>}

      {status === "error" && (
        <div className="banner error">
          <strong>Cannot reach backend.</strong>
          <p>{error}</p>
          <p className="muted">
            Start the API:{" "}
            <code>cd backend &amp;&amp; uvicorn src.api.main:app --reload --port 8000</code>
          </p>
        </div>
      )}

      {status === "ok" && health && (
        <ul className="health-list">
          <li>
            <span>Status</span>
            <strong>{health.status}</strong>
          </li>
          <li>
            <span>Data ready</span>
            <strong className={health.data_ready ? "ok" : "warn"}>
              {health.data_ready ? "Yes" : "No — run ingestion"}
            </strong>
          </li>
          <li>
            <span>Restaurants loaded</span>
            <strong>{health.restaurant_count ?? "—"}</strong>
          </li>
          <li>
            <span>Data path</span>
            <code className="path">{health.data_path}</code>
          </li>
        </ul>
      )}
    </section>
  );
}

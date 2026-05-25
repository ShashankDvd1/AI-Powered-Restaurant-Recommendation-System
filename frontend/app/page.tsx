import HealthStatus from "@/components/HealthStatus";

export default function Home() {
  return (
    <main>
      <header>
        <h1>Zomato AI Restaurant Recommendations</h1>
        <p>
          Phase 0 scaffold — backend health check. Recommendations arrive in Phase
          4.
        </p>
        <span className="badge">Phase 0 · Next.js + FastAPI</span>
      </header>
      <HealthStatus />
    </main>
  );
}

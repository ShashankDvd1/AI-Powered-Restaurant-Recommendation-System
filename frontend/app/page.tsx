"use client";

import React, { useState } from "react";
import PreferenceForm from "@/components/PreferenceForm";
import SummaryBlock from "@/components/SummaryBlock";
import RecommendationList from "@/components/RecommendationList";

interface RecommendationItem {
  restaurant_name: string;
  cuisine: string;
  rating: number;
  estimated_cost: string;
  explanation: string;
}

export default function Home() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [summary, setSummary] = useState<string | null>(null);
  const [recommendations, setRecommendations] = useState<RecommendationItem[] | null>(null);
  const [source, setSource] = useState<"grok" | "fallback">("fallback");

  const handleStartSubmit = () => {
    setLoading(true);
    setError(null);
    setSummary(null);
    setRecommendations(null);
  };

  const handleSubmitSuccess = (data: any) => {
    setLoading(false);
    setSummary(data.summary);
    setRecommendations(data.recommendations);
    setSource(data.meta?.source || "fallback");
  };

  const handleSubmitError = (errMsg: string) => {
    setLoading(false);
    setError(errMsg);
  };

  return (
    <main style={{ maxWidth: "1100px" }}>
      <header>
        <h1>Zomato AI Restaurant Recommendations</h1>
        <p>
          Configure preferences to discover restaurants matching your taste, backed by real Zomato data.
        </p>
      </header>

      <div className="dashboard-grid">
        {/* Left Column: Preference Form */}
        <div>
          <PreferenceForm
            onStartSubmit={handleStartSubmit}
            onSubmitSuccess={handleSubmitSuccess}
            onSubmitError={handleSubmitError}
            submitting={loading}
          />
        </div>

        {/* Right Column: Recommendations Results */}
        <div className="results-column">
          
          {/* Loading Skeleton */}
          {loading && (
            <div className="results-column">
              <div className="summary-panel skeleton-card">
                <div className="skeleton-pulse skeleton-title" style={{ width: "30%" }}></div>
                <div className="skeleton-pulse skeleton-text"></div>
                <div className="skeleton-pulse skeleton-text short"></div>
              </div>
              {[1, 2].map((i) => (
                <div key={i} className="restaurant-card skeleton-card">
                  <div className="skeleton-pulse skeleton-title"></div>
                  <div className="skeleton-pulse skeleton-text"></div>
                  <div className="skeleton-pulse skeleton-box"></div>
                </div>
              ))}
            </div>
          )}

          {/* Error Banner */}
          {error && (
            <div className="banner error">
              <strong>
                {error.toLowerCase().includes("location") || error.toLowerCase().includes("cuisine")
                  ? "Check Preferences"
                  : "Service Temporarily Busy"}
              </strong>
              <p>{error}</p>
            </div>
          )}

          {/* Results Summary & List */}
          {recommendations && recommendations.length > 0 && summary && (
            <>
              <SummaryBlock summary={summary} source={source} />
              <RecommendationList recommendations={recommendations} source={source} />
            </>
          )}

          {recommendations && recommendations.length === 0 && !loading && (
            <div className="banner error">
              <strong>No Results</strong>
              <p>No restaurants match your filters. Try lowering the minimum rating or selecting a different budget bucket.</p>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}

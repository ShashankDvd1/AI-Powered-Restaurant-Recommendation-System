"use client";

import React from "react";

interface RecommendationItem {
  restaurant_name: string;
  cuisine: string;
  rating: number;
  estimated_cost: string;
  explanation: string;
}

interface RecommendationListProps {
  recommendations: RecommendationItem[];
  source: "grok" | "fallback";
}

export default function RecommendationList({
  recommendations,
  source,
}: RecommendationListProps) {
  const isGrok = source === "grok";

  const getRatingClass = (rating: number) => {
    if (rating >= 4.0) return "high-rating";
    return "medium-rating";
  };

  return (
    <div className="results-column">
      {recommendations.map((rec, idx) => {
        // Split cuisines by comma for rendering individual badges
        const cuisinesList = rec.cuisine
          .split(",")
          .map((c) => c.trim())
          .filter((c) => c.length > 0);

        return (
          <div key={`${rec.restaurant_name}-${idx}`} className="restaurant-card">
            
            {/* Header: Title and Rating */}
            <div className="card-header-flex">
              <h3 className="restaurant-title">{rec.restaurant_name}</h3>
              <div className={`rating-badge-container ${getRatingClass(rec.rating)}`}>
                <span>★</span>
                <span>{rec.rating.toFixed(1)}</span>
              </div>
            </div>

            {/* Sub-row: Cuisines and Cost */}
            <div className="card-info-row">
              <div className="cuisine-tags-list">
                {cuisinesList.map((c) => (
                  <span key={c} className="cuisine-tag">
                    {c}
                  </span>
                ))}
              </div>
              <span className="muted">•</span>
              <span className="cost-label">Cost: {rec.estimated_cost}</span>
            </div>

            {/* Explanation box */}
            <div className="explanation-box">
              <span style={{ fontSize: "1.2rem", lineHeight: 0, verticalAlign: "middle", marginRight: "0.25rem", color: "var(--accent)" }}>“</span>
              {rec.explanation}
              <span style={{ fontSize: "1.2rem", lineHeight: 0, verticalAlign: "middle", marginLeft: "0.25rem", color: "var(--accent)" }}>”</span>
            </div>
          </div>
        );
      })}
    </div>
  );
}

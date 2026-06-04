"use client";

import React from "react";

interface SummaryBlockProps {
  summary: string;
  source: "grok" | "fallback";
}

export default function SummaryBlock({ summary, source }: SummaryBlockProps) {
  const isGrok = source === "grok";
  
  return (
    <div className={`summary-panel ${isGrok ? "grok" : "fallback"}`}>
      <div className="summary-header">
        <h3 style={{ color: isGrok ? "#d896ff" : "var(--warn)" }}>
          {isGrok ? "✨ AI Summary" : "⚠️ Fallback Overview"}
        </h3>
        <span className={`source-badge ${source}`}>
          {isGrok ? "Grok AI Ranked" : "Local Database"}
        </span>
      </div>
      <p className="summary-text">{summary}</p>
    </div>
  );
}

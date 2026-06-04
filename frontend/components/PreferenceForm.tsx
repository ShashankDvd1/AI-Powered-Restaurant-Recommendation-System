"use client";

import React, { useState, useEffect, useRef } from "react";
import { getApiUrl, getRecommendations, type RecommendationRequest } from "@/lib/api";

interface ApiErrorDetail {
  loc: (string | number)[];
  msg: string;
  type: string;
}

interface ApiResponseError {
  detail: string | ApiErrorDetail[];
}

interface PreferenceFormProps {
  onStartSubmit: () => void;
  onSubmitSuccess: (data: any) => void;
  onSubmitError: (error: string) => void;
  submitting: boolean;
}

export default function PreferenceForm({
  onStartSubmit,
  onSubmitSuccess,
  onSubmitError,
  submitting,
}: PreferenceFormProps) {
  const [locations, setLocations] = useState<string[]>([]);
  const [cuisines, setCuisines] = useState<string[]>([]);
  const [loadingMetadata, setLoadingMetadata] = useState(true);

  // Form fields
  const [locationSearch, setLocationSearch] = useState("");
  const [selectedLocation, setSelectedLocation] = useState("");
  const [cuisineSearch, setCuisineSearch] = useState("");
  const [selectedCuisine, setSelectedCuisine] = useState("");
  const [budget, setBudget] = useState<"low" | "medium" | "high">("medium");
  const [minRating, setMinRating] = useState(3.5);
  const [extraPreferences, setExtraPreferences] = useState("");
  const [topK, setTopK] = useState(5);

  // UI dropdown states
  const [showLocationDropdown, setShowLocationDropdown] = useState(false);
  const [showCuisineDropdown, setShowCuisineDropdown] = useState(false);

  // Refs for closing dropdowns on click outside
  const locationRef = useRef<HTMLDivElement>(null);
  const cuisineRef = useRef<HTMLDivElement>(null);

  const API_URL = getApiUrl();

  useEffect(() => {
    async function loadMetadata() {
      try {
        const [locRes, cuisRes] = await Promise.all([
          fetch(`${API_URL}/metadata/locations`),
          fetch(`${API_URL}/metadata/cuisines`),
        ]);

        if (locRes.ok && cuisRes.ok) {
          const locData = await locRes.json();
          const cuisData = await cuisRes.json();
          setLocations(locData);
          setCuisines(cuisData);
        }
      } catch (err) {
        console.error("Failed to load metadata dropdowns:", err);
      } finally {
        setLoadingMetadata(false);
      }
    }
    loadMetadata();
  }, [API_URL]);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (locationRef.current && !locationRef.current.contains(event.target as Node)) {
        setShowLocationDropdown(false);
      }
      if (cuisineRef.current && !cuisineRef.current.contains(event.target as Node)) {
        setShowCuisineDropdown(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  // Filter lists based on search terms
  const filteredLocations = locations.filter((loc) =>
    loc.toLowerCase().includes(locationSearch.toLowerCase())
  );

  const filteredCuisines = cuisines.filter((cuis) =>
    cuis.toLowerCase().includes(cuisineSearch.toLowerCase())
  );

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    onStartSubmit();

    // Client-side validations
    const locValue = selectedLocation || locationSearch.trim();
    const cuisValue = selectedCuisine || cuisineSearch.trim();

    if (!locValue) {
      onSubmitError("Location is required.");
      return;
    }
    if (!cuisValue) {
      onSubmitError("Cuisine is required.");
      return;
    }

    const payload: RecommendationRequest = {
      location: locValue,
      budget,
      cuisine: cuisValue,
      min_rating: minRating,
      extra_preferences: extraPreferences,
      top_k: topK,
    };

    try {
      const data = await getRecommendations(payload);
      onSubmitSuccess(data);
    } catch (err: any) {
      if (err.status === 422) {
        if (Array.isArray(err.detail)) {
          const errors = err.detail.map((e: any) => `${e.loc.slice(1).join(".")}: ${e.msg}`).join(" | ");
          onSubmitError(`Validation Error: ${errors}`);
        } else {
          onSubmitError(err.detail || "Invalid inputs.");
        }
      } else {
        onSubmitError(err.message || "Network error. Make sure the backend server is running.");
      }
    }
  };

  return (
    <div className="form-card">
      <h2>Preferences</h2>
      <form onSubmit={handleSubmit}>
        
        {/* Location Dropdown */}
        <div className="form-group" ref={locationRef}>
          <label className="form-label" htmlFor="location-input">Location</label>
          <input
            id="location-input"
            className="form-input"
            type="text"
            placeholder={loadingMetadata ? "Loading locations..." : "Select or type location..."}
            value={locationSearch}
            onChange={(e) => {
              setLocationSearch(e.target.value);
              setSelectedLocation("");
              setShowLocationDropdown(true);
            }}
            onFocus={() => setShowLocationDropdown(true)}
            disabled={loadingMetadata}
            autoComplete="off"
          />
          {showLocationDropdown && locationSearch && (
            <div className="autocomplete-dropdown">
              {filteredLocations.length > 0 ? (
                filteredLocations.map((loc) => (
                  <div
                    key={loc}
                    className="autocomplete-option"
                    onClick={() => {
                      setSelectedLocation(loc);
                      setLocationSearch(loc);
                      setShowLocationDropdown(false);
                    }}
                  >
                    {loc}
                  </div>
                ))
              ) : (
                <div className="autocomplete-no-results">No matches found. Will fuzzy check on submit.</div>
              )}
            </div>
          )}
        </div>

        {/* Cuisine Dropdown */}
        <div className="form-group" ref={cuisineRef}>
          <label className="form-label" htmlFor="cuisine-input">Cuisine</label>
          <input
            id="cuisine-input"
            className="form-input"
            type="text"
            placeholder={loadingMetadata ? "Loading cuisines..." : "Select or type cuisine..."}
            value={cuisineSearch}
            onChange={(e) => {
              setCuisineSearch(e.target.value);
              setSelectedCuisine("");
              setShowCuisineDropdown(true);
            }}
            onFocus={() => setShowCuisineDropdown(true)}
            disabled={loadingMetadata}
            autoComplete="off"
          />
          {showCuisineDropdown && cuisineSearch && (
            <div className="autocomplete-dropdown">
              {filteredCuisines.length > 0 ? (
                filteredCuisines.map((cuis) => (
                  <div
                    key={cuis}
                    className="autocomplete-option"
                    onClick={() => {
                      setSelectedCuisine(cuis);
                      setCuisineSearch(cuis);
                      setShowCuisineDropdown(false);
                    }}
                  >
                    {cuis}
                  </div>
                ))
              ) : (
                <div className="autocomplete-no-results">No matches found. Partial search allowed.</div>
              )}
            </div>
          )}
        </div>

        {/* Budget segmented selector */}
        <div className="form-group">
          <label className="form-label">Budget Range</label>
          <div className="budget-group">
            {(["low", "medium", "high"] as const).map((b) => (
              <button
                key={b}
                type="button"
                className={`budget-btn ${budget === b ? "active" : ""}`}
                onClick={() => setBudget(b)}
              >
                {b.charAt(0).toUpperCase() + b.slice(1)}
              </button>
            ))}
          </div>
        </div>

        {/* Min rating slider */}
        <div className="form-group">
          <label className="form-label" htmlFor="rating-slider">Minimum Rating</label>
          <div className="slider-container">
            <input
              id="rating-slider"
              className="slider-input"
              type="range"
              min="0.0"
              max="5.0"
              step="0.1"
              value={minRating}
              onChange={(e) => setMinRating(parseFloat(e.target.value))}
            />
            <span className="slider-val">{minRating.toFixed(1)}</span>
          </div>
        </div>

        {/* Extra preferences text area */}
        <div className="form-group">
          <label className="form-label" htmlFor="extra-prefs">Extra Preferences (Optional)</label>
          <textarea
            id="extra-prefs"
            className="form-textarea"
            rows={3}
            placeholder="e.g. rooftop seating, craft beers, kid friendly..."
            value={extraPreferences}
            onChange={(e) => setExtraPreferences(e.target.value)}
          />
        </div>

        {/* Top K select */}
        <div className="form-group">
          <label className="form-label" htmlFor="topk-select">Number of Recommendations</label>
          <select
            id="topk-select"
            className="form-select"
            value={topK}
            onChange={(e) => setTopK(parseInt(e.target.value))}
          >
            {[3, 5, 10, 15, 20].map((k) => (
              <option key={k} value={k}>
                Show {k} Restaurants
              </option>
            ))}
          </select>
        </div>

        <button className="submit-btn" type="submit" disabled={submitting || loadingMetadata}>
          {submitting ? "Searching..." : "Submit Preferences"}
        </button>
      </form>
    </div>
  );
}

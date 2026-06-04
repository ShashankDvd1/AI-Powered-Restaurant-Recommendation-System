import difflib
import logging
from typing import List, Dict, Any
import pandas as pd

from src.data.store import get_restaurant_dataframe

from src.filters.restaurant_filter import filter_restaurants
from src.models.preferences import UserPreferences
from src.models.recommendation import RecommendationItem, RecommendationMeta, RecommendationResponse
from src.llm import SYSTEM_PROMPT, build_user_prompt, call_grok_api, GrokAPIError, parse_grok_json_response

logger = logging.getLogger(__name__)

def get_recommendations(prefs: UserPreferences) -> RecommendationResponse:
    """
    Core pipeline orchestrating:
      load data -> filter -> LLM rank & explain -> grounding -> response.
      Falls back to rule-based ranking if LLM fails or API key is missing.
    """
    try:
        df = get_restaurant_dataframe()
    except Exception as err:
        logger.error(f"Failed to load dataset: {err}")
        return RecommendationResponse(
            summary="System error: dataset could not be loaded.",
            recommendations=[],
            meta=RecommendationMeta(candidate_count=0, source="fallback")
        )

    # 1. Filter candidates
    candidates_df = filter_restaurants(df, prefs)
    candidate_count = len(candidates_df)

    if candidates_df.empty:
        return RecommendationResponse(
            summary="No restaurants match all criteria. Try relaxing your filters (e.g. lowering minimum rating or expanding budget).",
            recommendations=[],
            meta=RecommendationMeta(candidate_count=0, source="fallback")
        )

    # Convert candidates to list of dicts for prompting & grounding
    candidates_list = candidates_df.to_dict(orient="records")

    try:
        # 2. Build prompt
        user_prompt = build_user_prompt(prefs, candidates_list)

        # 3. Call Grok API
        raw_completion = call_grok_api(SYSTEM_PROMPT, user_prompt)

        # 4. Parse JSON response
        parsed_data = parse_grok_json_response(raw_completion)

        # 5. Grounding Protocol
        # Create lookup map: lowercase_name -> candidate dict
        cand_map = {c["name"].lower().strip(): c for c in candidates_list}
        names_lower = list(cand_map.keys())

        grounded_items: List[RecommendationItem] = []
        for item in parsed_data["recommendations"]:
            name_query = item["restaurant_name"].lower().strip()
            matched_cand = None

            if name_query in cand_map:
                matched_cand = cand_map[name_query]
            else:
                # Fuzzy match if exact match fails
                matches = difflib.get_close_matches(name_query, names_lower, n=1, cutoff=0.6)
                if matches:
                    matched_cand = cand_map[matches[0]]

            if matched_cand:
                cost_val = matched_cand.get("approx_cost_for_two")
                cost_str = f"₹{int(cost_val)} for two" if cost_val and not pd.isna(cost_val) else "N/A"
                
                grounded_items.append(
                    RecommendationItem(
                        restaurant_name=matched_cand["name"],
                        cuisine=matched_cand["cuisines"] or "N/A",
                        rating=float(matched_cand["rating"]) if matched_cand.get("rating") else 3.5,
                        estimated_cost=cost_str,
                        explanation=item["explanation"]
                    )
                )

        if not grounded_items:
            raise ValueError("All recommendations returned by Grok were discarded by grounding checks.")

        # Cap output to requested top_k (just in case LLM returned more)
        final_recs = grounded_items[:prefs.top_k]

        return RecommendationResponse(
            summary=parsed_data["summary"],
            recommendations=final_recs,
            meta=RecommendationMeta(candidate_count=candidate_count, source="grok")
        )

    except (GrokAPIError, Exception) as err:
        logger.warning(f"Grok recommendation failed, triggering fallback engine. Error: {err}")
        return _run_fallback_engine(candidates_list, prefs, candidate_count)


def _run_fallback_engine(candidates: List[Dict[str, Any]], prefs: UserPreferences, total_candidates: int) -> RecommendationResponse:
    """Rule-based fallback: returns top-K candidates directly from dataset."""
    fallback_recs: List[RecommendationItem] = []
    
    # Candidates are already sorted by rating desc and votes desc
    top_candidates = candidates[:prefs.top_k]

    for cand in top_candidates:
        cost_val = cand.get("approx_cost_for_two")
        cost_str = f"₹{int(cost_val)} for two" if cost_val and not pd.isna(cost_val) else "N/A"
        
        explanation = (
            f"Highly rated {cand['cuisines']} restaurant in {cand['location'] or prefs.location} "
            f"matching your {prefs.budget} budget. (Rating: {cand['rating']}, Votes: {cand['votes']})"
        )

        fallback_recs.append(
            RecommendationItem(
                restaurant_name=cand["name"],
                cuisine=cand["cuisines"] or "N/A",
                rating=float(cand["rating"]) if cand.get("rating") else 3.5,
                estimated_cost=cost_str,
                explanation=explanation
            )
        )

    summary = (
        f"Displaying top {len(fallback_recs)} matched restaurants directly from database "
        f"(AI service currently unavailable)."
    )

    return RecommendationResponse(
        summary=summary,
        recommendations=fallback_recs,
        meta=RecommendationMeta(candidate_count=total_candidates, source="fallback")
    )

from src.models.preferences import UserPreferences

SYSTEM_PROMPT = """You are the Zomato Food Recommendation Assistant, a specialized AI designed to rank and explain restaurant recommendations.

CRITICAL INSTRUCTIONS:
1. You MUST select and recommend restaurants ONLY from the provided candidate list.
2. DO NOT invent or hallucinate any restaurants, addresses, ratings, or costs.
3. Every recommendation you output MUST match a restaurant in the provided candidates list.
4. Your response MUST be a single, valid JSON object matching the schema below.

JSON Response Schema:
{
  "summary": "A concise one-paragraph overview explaining why these restaurants were selected based on the user's preferences.",
  "recommendations": [
    {
      "restaurant_name": "Exact name of the restaurant from the candidate list",
      "cuisine": "Cuisines matching the candidate list",
      "rating": 4.5,
      "estimated_cost": "Estimated cost from the candidate list",
      "explanation": "A personalized 1-2 sentence explanation of why this restaurant matches the user's location, budget, rating, and extra preferences."
    }
  ]
}
"""

def build_user_prompt(prefs: UserPreferences, candidates: list[dict]) -> str:
    """Build the user prompt compiling preferences and candidates."""
    candidate_lines = []
    for idx, cand in enumerate(candidates):
        cost_str = f"₹{cand['approx_cost_for_two']}" if cand.get('approx_cost_for_two') else "N/A"
        candidate_lines.append(
            f"Index {idx}: Name: {cand['name']} | Cuisine: {cand['cuisines']} | Rating: {cand['rating']} | Cost for two: {cost_str} | Address: {cand.get('address', 'N/A')}"
        )
    candidates_str = "\n".join(candidate_lines)

    user_prompt = f"""User Preferences:
- Location: {prefs.location}
- Budget Range: {prefs.budget}
- Preferred Cuisine: {prefs.cuisine}
- Minimum Rating: {prefs.min_rating}
- Extra Preferences: {prefs.extra_preferences or 'None'}
- Top K to show: {prefs.top_k}

Candidate Restaurants List (Total: {len(candidates)}):
{candidates_str}

Task:
Please select the best {prefs.top_k} restaurants from the Candidate Restaurants List that best fit the User Preferences. Provide a summary paragraph at the top and a list of recommendations with personalized explanations.
"""
    return user_prompt

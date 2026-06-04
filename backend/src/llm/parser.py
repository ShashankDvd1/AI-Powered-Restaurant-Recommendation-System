import json
import re
from typing import Any, Dict

def parse_grok_json_response(content: str) -> Dict[str, Any]:
    """
    Parse the string JSON returned by Grok and validate fields.
    Attempts basic regex cleaning if markdown blocks or trailing commas exist.
    """
    cleaned = content.strip()
    
    # Strip markdown block wraps if present (e.g. ```json ... ```)
    if cleaned.startswith("```"):
        # Match anything inside ```json ... ```
        match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned)
        if match:
            cleaned = match.group(1).strip()

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as err:
        raise ValueError(f"Failed to parse Grok output as JSON: {err}. Output was: {content}")

    # Ensure required keys exist
    if not isinstance(data, dict):
        raise ValueError("Grok response must be a JSON object dictionary.")

    if "summary" not in data:
        data["summary"] = "AI recommendations based on your preferences."
        
    if "recommendations" not in data or not isinstance(data["recommendations"], list):
        raise ValueError("Grok response missing 'recommendations' list array.")

    # Validate individual items
    valid_recs = []
    for item in data["recommendations"]:
        if not isinstance(item, dict) or "restaurant_name" not in item:
            continue
        
        # Clean defaults if missing
        restaurant_name = str(item.get("restaurant_name", "")).strip()
        if not restaurant_name:
            continue

        valid_recs.append({
            "restaurant_name": restaurant_name,
            "cuisine": str(item.get("cuisine", "N/A")),
            "rating": float(item.get("rating") if item.get("rating") is not None else 3.5),
            "estimated_cost": str(item.get("estimated_cost", "N/A")),
            "explanation": str(item.get("explanation", "Matches your tastes.")),
        })

    data["recommendations"] = valid_recs
    return data

import pandas as pd
from src.models.preferences import UserPreferences

def filter_restaurants(df: pd.DataFrame, prefs: UserPreferences) -> pd.DataFrame:
    """
    Filter dataset restaurants based on user preferences.
    Sorts by rating desc, then votes desc. Caps candidates at 30 rows.
    """
    # 1. Location match (case-insensitive city)
    city_match = df["city"].str.lower() == prefs.location.lower()
    filtered = df[city_match]

    if filtered.empty:
        return filtered

    # 2. Budget bucket match
    budget_match = filtered["budget_bucket"].str.lower() == prefs.budget.lower()
    filtered = filtered[budget_match]

    if filtered.empty:
        return filtered

    # 3. Rating threshold match
    rating_match = filtered["rating"] >= prefs.min_rating
    filtered = filtered[rating_match]

    if filtered.empty:
        return filtered

    # 4. Cuisine match (substring check, case-insensitive)
    cuisine_match = filtered["cuisines"].str.lower().str.contains(prefs.cuisine.lower(), na=False)
    filtered = filtered[cuisine_match]

    if filtered.empty:
        return filtered

    # 5. Rank: sort by rating desc, then votes desc
    sorted_df = filtered.sort_values(by=["rating", "votes"], ascending=[False, False])

    # 6. Cap candidates
    return sorted_df.head(30).reset_index(drop=True)

import json
import math
import os


def load_data(filepath="data.json"):
    """Load the content database from a JSON file and return a list of dicts."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Data file '{filepath}' not found.")
    with open(filepath, "r") as f:
        data = json.load(f)
    if not isinstance(data, list) or len(data) == 0:
        raise ValueError("Data file must contain a non-empty JSON array.")
    return data


def collect_all_features(database):
    """
    Scan the database and return a sorted list of every unique feature value.

    Features are drawn from: genres, themes, tone, mood, pace, and complexity.
    List-type fields contribute each element; scalar fields contribute their value.
    """
    features = set()
    for item in database:
        for genre in item.get("genres", []):
            features.add(f"genre:{genre}")
        for theme in item.get("themes", []):
            features.add(f"theme:{theme}")
        for tone in item.get("tone", []):
            features.add(f"tone:{tone}")
        features.add(f"mood:{item.get('mood', '')}")
        features.add(f"pace:{item.get('pace', '')}")
        features.add(f"complexity:{item.get('complexity', '')}")
    return sorted(features)


def build_feature_vector(item, all_features):
    """
    Convert a single content item into a binary feature vector.

    Each position corresponds to a feature from all_features.
    A 1 means the item possesses that feature; 0 means it does not.
    """
    item_features = set()
    for genre in item.get("genres", []):
        item_features.add(f"genre:{genre}")
    for theme in item.get("themes", []):
        item_features.add(f"theme:{theme}")
    for tone in item.get("tone", []):
        item_features.add(f"tone:{tone}")
    item_features.add(f"mood:{item.get('mood', '')}")
    item_features.add(f"pace:{item.get('pace', '')}")
    item_features.add(f"complexity:{item.get('complexity', '')}")

    return [1 if f in item_features else 0 for f in all_features]


def cosine_similarity(vec_a, vec_b):
    """
    Compute the cosine similarity between two numeric vectors.

    Returns a float between 0.0 and 1.0.  Returns 0.0 if either vector
    has zero magnitude (avoids division-by-zero).
    """
    if len(vec_a) != len(vec_b):
        raise ValueError("Vectors must be the same length.")

    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    mag_a = math.sqrt(sum(a * a for a in vec_a))
    mag_b = math.sqrt(sum(b * b for b in vec_b))

    if mag_a == 0 or mag_b == 0:
        return 0.0

    return dot / (mag_a * mag_b)


def build_profile_vector(liked_items, all_features):
    """
    Build an aggregate preference vector from a list of liked items.

    For each feature, sums the binary values across all liked items and
    normalises so the resulting vector has unit magnitude. This gives
    features that appear in multiple liked items proportionally more weight.
    """
    profile = [0] * len(all_features)
    for item in liked_items:
        vec = build_feature_vector(item, all_features)
        for i in range(len(profile)):
            profile[i] += vec[i]

    mag = math.sqrt(sum(v * v for v in profile))
    if mag > 0:
        profile = [v / mag for v in profile]
    return profile


def get_recommendations(liked_items, database, n=5):
    """
    Return the top-n recommended items from the database.

    Builds a user profile from liked_items, then ranks every item in the
    database by cosine similarity to that profile.  Items already in the
    liked list are excluded from results.
    """
    all_features = collect_all_features(database)
    profile = build_profile_vector(liked_items, all_features)

    liked_titles = {item["title"].lower() for item in liked_items}
    scored = []

    for item in database:
        if item["title"].lower() in liked_titles:
            continue
        vec = build_feature_vector(item, all_features)
        score = cosine_similarity(profile, vec)
        scored.append((item, score))

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:n]


def search_items(query, database):
    """
    Search for items whose title contains the query string (case-insensitive).

    Returns a list of matching item dicts.
    """
    query_lower = query.strip().lower()
    return [item for item in database if query_lower in item["title"].lower()]


def format_item(item):
    """Return a short one-line description of a content item."""
    kind = item.get("type", "unknown").capitalize()
    author = item.get("author", "Unknown")
    return f"{item['title']} ({kind} by {author})"


def format_item_detail(item):
    """Return a multi-line detailed description of a content item."""
    lines = []
    kind = item.get("type", "unknown").capitalize()
    lines.append(f"  Title:      {item['title']}")
    lines.append(f"  Type:       {kind}")
    lines.append(f"  Creator:    {item.get('author', 'Unknown')}")
    lines.append(f"  Genres:     {', '.join(item.get('genres', []))}")
    lines.append(f"  Themes:     {', '.join(item.get('themes', []))}")
    lines.append(f"  Tone:       {', '.join(item.get('tone', []))}")
    lines.append(f"  Mood:       {item.get('mood', 'N/A')}")
    lines.append(f"  Pace:       {item.get('pace', 'N/A')}")
    lines.append(f"  Complexity: {item.get('complexity', 'N/A')}")
    return "\n".join(lines)


def get_shared_attributes(liked_items, recommendation):
    """
    Identify the attributes shared between a recommended item and the
    user's liked items.  Returns a list of human-readable reason strings.
    """
    reasons = []
    liked_genres = set()
    liked_themes = set()
    liked_tones = set()
    liked_moods = set()

    for item in liked_items:
        liked_genres.update(item.get("genres", []))
        liked_themes.update(item.get("themes", []))
        liked_tones.update(item.get("tone", []))
        liked_moods.add(item.get("mood", ""))

    shared_themes = liked_themes & set(recommendation.get("themes", []))
    shared_tones = liked_tones & set(recommendation.get("tone", []))
    shared_genres = liked_genres & set(recommendation.get("genres", []))

    if shared_themes:
        reasons.append(f"Shared themes: {', '.join(sorted(shared_themes))}")
    if shared_tones:
        reasons.append(f"Similar tone: {', '.join(sorted(shared_tones))}")
    if shared_genres:
        reasons.append(f"Genre overlap: {', '.join(sorted(shared_genres))}")
    if recommendation.get("mood", "") in liked_moods:
        reasons.append(f"Matching mood: {recommendation['mood']}")

    return reasons

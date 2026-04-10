import json
import math
import os


def load_data(filepath="data.json"):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Data file '{filepath}' not found.")
    with open(filepath, "r") as f:
        return json.load(f)

def collect_all_features(database):
    features = set()
    for item in database:
        for g in item.get("genres", []):
            features.add(f"genre:{g}")
        for t in item.get("themes", []):
            features.add(f"theme:{t}")
        for t in item.get("tone", []):
            features.add(f"tone:{t}")
        features.add(f"mood:{item.get('mood', '')}")
        features.add(f"pace:{item.get('pace', '')}")
        features.add(f"complexity:{item.get('complexity', '')}")
    return sorted(features)

def build_feature_vector(item, all_features):
    item_features = set()
    for g in item.get("genres", []):
        item_features.add(f"genre:{g}")
    for t in item.get("themes", []):
        item_features.add(f"theme:{t}")
    for t in item.get("tone", []):
        item_features.add(f"tone:{t}")
    item_features.add(f"mood:{item.get('mood', '')}")
    item_features.add(f"pace:{item.get('pace', '')}")
    item_features.add(f"complexity:{item.get('complexity', '')}")
    return [1 if f in item_features else 0 for f in all_features]


def cosine_similarity(vec_a, vec_b):
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    mag_a = math.sqrt(sum(a * a for a in vec_a))
    mag_b = math.sqrt(sum(b * b for b in vec_b))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


def get_recommendations(liked_items, database, n=3):
    all_features = collect_all_features(database)

    profile = [0] * len(all_features)
    for item in liked_items:
        vec = build_feature_vector(item, all_features)
        for i in range(len(profile)):
            profile[i] += vec[i]

    mag = math.sqrt(sum(v * v for v in profile))
    if mag > 0:
        profile = [v / mag for v in profile]

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
    query = query.strip().lower()
    return [item for item in database if query in item["title"].lower()]

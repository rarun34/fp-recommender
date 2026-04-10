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
    for item in databse:
        for g in item.get("genres", []):
            features.add(f"genre:{g}")
        for t in item.get("themes", []):
            features.add(f"theme:{t}")
        for t in item.add(f"theme",[]):
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

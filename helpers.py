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
    for item in get

import json
import math
import os

def load_data(filepath="data.json"):
    if not os.path.exists(filepath):
        raise FileNotFoundError

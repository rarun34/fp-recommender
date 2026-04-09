import json
import os
import pytest
from helpers import (
    load_data,
    collect_all_features,
    build_feature_vector,
    cosine_similarity,
    build_profile_vector,
    get_recommendations,
    search_items,
    format_item,
    format_item_detail,
    get_shared_attributes,
)


SAMPLE_DATA = [
    {
        "title": "Alpha",
        "type": "book",
        "author": "Author A",
        "genres": ["fantasy", "adventure"],
        "themes": ["courage", "friendship"],
        "tone": ["warm", "epic"],
        "mood": "uplifting",
        "pace": "fast",
        "complexity": "easy",
    },
    {
        "title": "Beta",
        "type": "movie",
        "author": "Director B",
        "genres": ["fantasy", "drama"],
        "themes": ["courage", "sacrifice"],
        "tone": ["epic", "dark"],
        "mood": "grand",
        "pace": "moderate",
        "complexity": "moderate",
    },
    {
        "title": "Gamma",
        "type": "book",
        "author": "Author C",
        "genres": ["thriller", "mystery"],
        "themes": ["deception", "justice"],
        "tone": ["tense", "dark"],
        "mood": "unsettling",
        "pace": "fast",
        "complexity": "moderate",
    },
    {
        "title": "Delta",
        "type": "movie",
        "author": "Director D",
        "genres": ["romance", "drama"],
        "themes": ["love", "personal growth"],
        "tone": ["warm", "reflective"],
        "mood": "charming",
        "pace": "slow",
        "complexity": "easy",
    },
]


@pytest.fixture
def sample_db():
    return SAMPLE_DATA


@pytest.fixture
def all_features(sample_db):
    return collect_all_features(sample_db)


def test_load_data_returns_list():
    data = load_data()
    assert isinstance(data, list)
    assert len(data) > 0


def test_load_data_items_have_required_keys():
    required = {"title", "type", "author", "genres", "themes", "tone", "mood", "pace", "complexity"}
    data = load_data()
    for item in data:
        assert required.issubset(item.keys())


def test_load_data_missing_file():
    with pytest.raises(FileNotFoundError):
        load_data("nonexistent_file.json")


def test_collect_all_features_sorted(sample_db):
    feats = collect_all_features(sample_db)
    assert feats == sorted(feats)


def test_collect_all_features_no_duplicates(sample_db):
    feats = collect_all_features(sample_db)
    assert len(feats) == len(set(feats))


def test_feature_vector_length(sample_db, all_features):
    vec = build_feature_vector(sample_db[0], all_features)
    assert len(vec) == len(all_features)


def test_feature_vector_binary(sample_db, all_features):
    vec = build_feature_vector(sample_db[0], all_features)
    assert all(v in (0, 1) for v in vec)


def test_cosine_identical_vectors():
    assert cosine_similarity([1, 0, 1], [1, 0, 1]) == pytest.approx(1.0)


def test_cosine_orthogonal_vectors():
    assert cosine_similarity([1, 0, 0], [0, 1, 0]) == pytest.approx(0.0)


def test_cosine_zero_vector():
    assert cosine_similarity([0, 0, 0], [1, 1, 1]) == 0.0


def test_recommendations_returns_correct_count(sample_db):
    liked = [sample_db[0]]
    recs = get_recommendations(liked, sample_db, n=2)
    assert len(recs) == 2


def test_recommendations_ordered_by_score(sample_db):
    liked = [sample_db[0]]
    recs = get_recommendations(liked, sample_db, n=3)
    scores = [score for _, score in recs]
    assert scores == sorted(scores, reverse=True)


def test_search_exact_match(sample_db):
    results = search_items("Alpha", sample_db)
    assert len(results) == 1


def test_search_case_insensitive(sample_db):
    results = search_items("alpha", sample_db)
    assert len(results) == 1


def test_search_no_match(sample_db):
    results = search_items("zzzzz", sample_db)
    assert len(results) == 0


def test_format_item(sample_db):
    result = format_item(sample_db[0])
    assert "Alpha" in result
    assert "Book" in result


def test_shared_attributes_finds_overlap(sample_db):
    liked = [sample_db[0]]
    rec = sample_db[1]
    reasons = get_shared_attributes(liked, rec)
    combined = " ".join(reasons)
    assert "courage" in combined

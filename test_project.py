import pytest
from helpers import load_data, cosine_similarity, get_recommendations, search_items, collect_all_features, build_feature_vector


def test_load_data():
    data = load_data()
    assert isinstance(data, list)
    assert len(data) > 0


def test_load_data_missing_file():
    with pytest.raises(FileNotFoundError):
        load_data("fake.json")


def test_cosine_identical():
    assert cosine_similarity([1, 0, 1], [1, 0, 1]) == pytest.approx(1.0)


def test_cosine_orthogonal():
    assert cosine_similarity([1, 0, 0], [0, 1, 0]) == pytest.approx(0.0)


def test_cosine_zero_vector():
    assert cosine_similarity([0, 0, 0], [1, 1, 1]) == 0.0


def test_search_found():
    data = load_data()
    results = search_items("1984", data)
    assert len(results) == 1


def test_search_partial():
    data = load_data()
    results = search_items("great", data)
    assert len(results) == 1


def test_search_not_found():
    data = load_data()
    results = search_items("zzzzz", data)
    assert len(results) == 0


def test_recommendations_count():
    data = load_data()
    liked = [data[0]]
    recs = get_recommendations(liked, data, n=3)
    assert len(recs) == 3


def test_recommendations_excludes_liked():
    data = load_data()
    liked = [data[0]]
    recs = get_recommendations(liked, data, n=5)
    rec_titles = [item["title"] for item, _ in recs]
    assert data[0]["title"] not in rec_titles

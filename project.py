import sys
from helpers import load_data, get_recommendations, search_items


def main():
    print("\n=== Narrative-Based Content Recommender ===\n")

    database = load_data()
    liked = gather_likes(database)

    if not liked:
        print("No items selected. Goodbye!")
        sys.exit(0)

    print("\nYou liked:")
    for item in liked:
        print(f"  - {item['title']} ({item['type']})")

    results = get_recommendations(liked, database, n=3)

    print("\n=== Recommendations ===\n")
    for rank, (item, score) in enumerate(results, 1):
        pct = round(score * 100)
        print(f"  {rank}. {item['title']} ({item['type']} by {item['author']}) - {pct}% match")
        shared = find_shared_themes(liked, item)
        if shared:
            print(f"     Why: shared themes - {', '.join(shared)}")

    print("\nDone!")


def gather_likes(database):
    liked = []
    print("Available items:")
    for i, item in enumerate(database, 1):
        print(f"  {i}. {item['title']} ({item['type']})")

    print(f"\nPick 1-3 items by number (comma-separated):")
    try:
        choices = input("> ").strip()
    except (EOFError, KeyboardInterrupt):
        return liked

    for part in choices.split(","):
        part = part.strip()
        if part.isdigit():
            idx = int(part) - 1
            if 0 <= idx < len(database) and database[idx] not in liked:
                liked.append(database[idx])

    return liked


def find_shared_themes(liked_items, recommendation):
    liked_themes = set()
    for item in liked_items:
        liked_themes.update(item.get("themes", []))
    shared = liked_themes & set(recommendation.get("themes", []))
    return sorted(shared)


if __name__ == "__main__":
    main()

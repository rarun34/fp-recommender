import sys
from helpers import (
    load_data,
    search_items,
    format_item,
    format_item_detail,
    get_recommendations,
    get_shared_attributes,
)


BANNER = r"""
 ___  ___  ___  ___  ___  ___  ___  ___  ___  ___  ___  ___
|   ||   ||   ||   ||   ||   ||   ||   ||   ||   ||   ||   |
| N || A || R || R || A || T || I || V || E ||   ||   ||   |
|___||___||___||___||___||___||___||___||___||___||___||___|

  Narrative-Based Content Recommendation System
  Discover books & movies that *feel* like the ones you love.
"""


def main():
    print(BANNER)

    database = load_data()
    liked = gather_likes(database)

    if not liked:
        print("\nYou didn't select any items. Goodbye!")
        sys.exit(0)

    print(f"\n{'=' * 56}")
    print("  YOUR SELECTIONS")
    print(f"{'=' * 56}")
    for item in liked:
        print(f"  * {format_item(item)}")

    results = get_recommendations(liked, database, n=5)
    display_recommendations(results, liked)

    print("\nThanks for using the Narrative Recommender. Enjoy!")


def gather_likes(database):
    liked = []
    print("Tell me up to 3 books or movies you enjoy.")
    print("I'll use your choices to recommend similar content.\n")
    print("Commands:  search <query>  |  list  |  done\n")

    while len(liked) < 3:
        prompt = f"[{len(liked)}/3 selected] > "
        try:
            user_input = input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not user_input:
            continue

        command = user_input.lower()

        if command == "done":
            break

        elif command == "list":
            print_catalog(database)

        elif command.startswith("search "):
            query = user_input[7:]
            handle_search(query, database, liked)

        else:
            handle_search(user_input, database, liked)

    return liked


def print_catalog(database):
    books = [i for i in database if i["type"] == "book"]
    movies = [i for i in database if i["type"] == "movie"]

    print(f"\n{'─' * 50}")
    print(f"  BOOKS ({len(books)} available)")
    print(f"{'─' * 50}")
    for i, item in enumerate(books, 1):
        print(f"  {i:>2}. {format_item(item)}")

    print(f"\n{'─' * 50}")
    print(f"  MOVIES ({len(movies)} available)")
    print(f"{'─' * 50}")
    for i, item in enumerate(movies, 1):
        print(f"  {i:>2}. {format_item(item)}")
    print()


def handle_search(query, database, liked):
    results = search_items(query, database)

    if not results:
        print(f"  No results for '{query}'. Try 'list' to see all items.\n")
        return

    print(f"\n  Found {len(results)} result(s):")
    for i, item in enumerate(results, 1):
        already = " [already selected]" if item in liked else ""
        print(f"    {i}. {format_item(item)}{already}")

    print(f"  Enter a number to select, or press Enter to skip.")

    try:
        choice = input("  Pick > ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return

    if not choice.isdigit():
        return

    idx = int(choice) - 1
    if 0 <= idx < len(results):
        selected = results[idx]
        if selected in liked:
            print(f"  '{selected['title']}' is already in your list.\n")
        else:
            liked.append(selected)
            print(f"  Added '{selected['title']}'\n")
    else:
        print("  Invalid number.\n")


def display_recommendations(results, liked):
    print(f"\n{'=' * 56}")
    print("  YOUR RECOMMENDATIONS")
    print(f"{'=' * 56}")

    if not results:
        print("  No recommendations found. Try different selections!")
        return

    for rank, (item, score) in enumerate(results, 1):
        pct = round(score * 100)
        print(f"\n  #{rank}  {item['title']}  ({pct}% match)")
        print(f"  {'─' * 48}")
        print(format_item_detail(item))

        reasons = get_shared_attributes(liked, item)
        if reasons:
            print(f"  Why this?  {'; '.join(reasons)}")

    print(f"\n{'=' * 56}")


if __name__ == "__main__":
    main()

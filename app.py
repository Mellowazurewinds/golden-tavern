"""Golden Tavern: a small Flask front end for TheMealDB."""

from __future__ import annotations

import json
import re
from functools import lru_cache
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

from flask import Flask, jsonify, render_template, request

try:
    # Cloudflare Workers provides Fetch instead of regular outbound sockets.
    from pyodide.ffi import run_sync
    from workers import fetch as worker_fetch
except ImportError:
    run_sync = None
    worker_fetch = None

app = Flask(__name__)

MEALDB_URL = "https://www.themealdb.com/api/json/v1/1/"


def mealdb(path: str, **params: str) -> dict:
    """Fetch a JSON response from TheMealDB with a short timeout."""
    url = f"{MEALDB_URL}{path}?{urlencode(params)}"
    if worker_fetch is not None:
        try:
            response = run_sync(worker_fetch(url))
            if not response.ok:
                raise RuntimeError(f"TheMealDB returned HTTP {response.status}.")
            payload = run_sync(response.json())
            return payload.to_py() if hasattr(payload, "to_py") else payload
        except RuntimeError:
            raise
        except Exception as exc:
            app.logger.warning("TheMealDB Worker request failed: %s", exc)
            raise RuntimeError("Recipe service is unavailable right now. Please try again in a moment.") from exc
    try:
        with urlopen(url, timeout=8) as response:
            return json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        app.logger.warning("TheMealDB request failed: %s", exc)
        raise RuntimeError("Recipe service is unavailable right now. Please try again in a moment.") from exc


def normalized_ingredient(name: str) -> str:
    return re.sub(r"\s+", " ", name.replace("_", " ").strip().lower())


@lru_cache(maxsize=1)
def ingredient_catalog() -> tuple[str, ...]:
    """Cache TheMealDB's ingredient names to recognize phrases without commas."""
    meals = mealdb("list.php", i="list").get("meals") or []
    return tuple(sorted(
        {normalized_ingredient(meal.get("strIngredient", "")) for meal in meals if meal.get("strIngredient")},
        key=lambda name: (-len(name.split()), -len(name), name),
    ))


def parse_ingredients(query: str) -> list[str]:
    """Split explicit separators, or recognize ingredient names in plain text."""
    explicit_parts = [part.strip() for part in re.split(r"\s*(?:,|;|\+)\s*", query) if part.strip()]
    if len(explicit_parts) > 1:
        return list(dict.fromkeys(normalized_ingredient(part) for part in explicit_parts))

    words = re.sub(r"\band\b", " ", query.lower()).split()
    try:
        catalog = ingredient_catalog()
    except RuntimeError:
        # Still allow simple space-separated searches if the catalog endpoint is down.
        catalog = ()
    found: list[str] = []
    index = 0
    while index < len(words):
        match = next((name for name in catalog if words[index:index + len(name.split())] == name.split()), None)
        if match:
            found.append(match)
            index += len(match.split())
        else:
            # Unknown words still get a chance to match TheMealDB's ingredient filter.
            found.append(words[index])
            index += 1
    return list(dict.fromkeys(found))


@app.get("/")
def home():
    return render_template("index.html")


@app.get("/api/meals")
def search_meals():
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({"meals": []})

    try:
        ingredients = parse_ingredients(query)
        if len(ingredients) > 1:
            if len(ingredients) > 6:
                return jsonify({"error": "Search up to six ingredients at a time."}), 400

            # Require a recipe to appear in every ingredient filter result.
            # This prevents unrelated matches for searches like "chicken chocolate".
            results_by_ingredient = [
                mealdb("filter.php", i=ingredient.replace(" ", "_")).get("meals") or []
                for ingredient in ingredients
            ]

            common_ids = {meal["idMeal"] for meal in results_by_ingredient[0]}
            for ingredient_meals in results_by_ingredient[1:]:
                common_ids.intersection_update(meal["idMeal"] for meal in ingredient_meals)
            meals = [meal for meal in results_by_ingredient[0] if meal["idMeal"] in common_ids]
            return jsonify({"meals": meals[:24]})

        # With one search term, try it as a dish name first, then as an ingredient.
        named_meals = mealdb("search.php", s=query).get("meals") or []
        if named_meals:
            return jsonify({"meals": named_meals[:24]})
        meals = mealdb("filter.php", i=ingredients[0].replace(" ", "_")).get("meals") or []
        return jsonify({"meals": meals})
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 502


@app.get("/api/categories/<category>")
def category_meals(category: str):
    try:
        meals = mealdb("filter.php", c=category).get("meals") or []
        return jsonify({"meals": meals})
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 502


@app.get("/api/meals/random")
def random_meal():
    try:
        meals = mealdb("random.php").get("meals") or []
        return jsonify({"meals": meals})
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 502


@app.get("/api/meals/<meal_id>")
def meal_details(meal_id: str):
    try:
        meals = mealdb("lookup.php", i=meal_id).get("meals") or []
        if not meals:
            return jsonify({"error": "That recipe could not be found."}), 404
        return jsonify(meals[0])
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 502


if __name__ == "__main__":
    import threading
    import webbrowser

    url = "http://127.0.0.1:5000"
    threading.Timer(0.8, webbrowser.open, args=(url,)).start()
    print(f"Golden Tavern is running at {url}. Close this window to stop it.")
    app.run(host="127.0.0.1", port=5000, debug=False)

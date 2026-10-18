"""Golden Tavern: a small Flask front end for TheMealDB."""

from __future__ import annotations

import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

MEALDB_URL = "https://www.themealdb.com/api/json/v1/1/"


def mealdb(path: str, **params: str) -> dict:
    """Fetch a JSON response from TheMealDB with a short timeout."""
    url = f"{MEALDB_URL}{path}?{urlencode(params)}"
    try:
        with urlopen(url, timeout=8) as response:
            return json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        app.logger.warning("TheMealDB request failed: %s", exc)
        raise RuntimeError("Recipe service is unavailable right now. Please try again in a moment.") from exc


@app.get("/")
def home():
    return render_template("index.html")


@app.get("/api/meals")
def search_meals():
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({"meals": []})
    try:
        meals = mealdb("search.php", s=query).get("meals") or []
        # If it is not a dish name, try it as a single ingredient.
        if not meals:
            meals = mealdb("filter.php", i=query).get("meals") or []
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
    app.run(debug=True)

# Golden Tavern

Golden Tavern is a calm, recipe-discovery site for finding something good to cook. It uses Python, Flask, HTML, CSS, vanilla JavaScript, and [TheMealDB](https://www.themealdb.com/).

## Run it locally

To start Golden Tavern, double-click `run_golden_tavern.bat` in this folder. It opens the site in your browser. Keep the console window open while using the app; close it to stop the server.

To build `GoldenTavern.exe`, double-click `build_golden_tavern.bat`. The first build downloads the packaging tools and may take a few minutes.

The launcher prepares Flask if needed, then opens the app in your browser.

The launchers prefer the Python runtime bundled with Codex, then try installed Python. Golden Tavern listens only on this computer at [http://127.0.0.1:5000](http://127.0.0.1:5000). The recipe search uses TheMealDB and therefore needs an internet connection.

For a manual source run, install Python 3.10 or newer, then run `python -m pip install -r requirements-local.txt` and `python app.py` from this folder.

## Deploy to Cloudflare

Cloudflare Workers Builds can deploy the Flask app from the connected GitHub repository. Your computer does not need Node.js or `uv` for this workflow. Cloudflare's build image provides these tools.

In the Cloudflare project setup, use this build command:

```sh
uv run pywrangler sync && python build_cloudflare.py
```

Use the default deploy command, `npx wrangler deploy`. Cloudflare will install the Worker packages, prepare the static page files, and deploy whenever a commit reaches the connected branch.

## What is here

- `app.py` serves the page and makes recipe requests to TheMealDB.
- `templates/index.html` contains the accessible page structure.
- `static/styles.css` holds the responsive Warm Ivory, Forest Green, and Terracotta design.
- `static/app.js` powers recipe search, quick categories, random inspiration, and recipe details.

The search box accepts a dish name or ingredients. For multiple ingredients, it only returns recipes that match every ingredient. The API is free to explore and does not need a key.

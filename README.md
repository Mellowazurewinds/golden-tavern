# Golden Tavern

Golden Tavern is a calm, recipe-discovery site for finding something good to cook. It uses Python, Flask, HTML, CSS, vanilla JavaScript, and [TheMealDB](https://www.themealdb.com/).

## Run it locally

1. Install Python 3.10 or newer.
2. Open a terminal in this folder.
3. Create and activate a virtual environment:

   ```powershell
   py -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

4. Install the one dependency and start the site:

   ```powershell
   py -m pip install -r requirements.txt
   py app.py
   ```

5. Open http://127.0.0.1:5000 in your browser.

On macOS or Linux, activate the environment with `source .venv/bin/activate` and use `python3` in place of `py`.

## What is here

- `app.py` serves the page and makes recipe requests to TheMealDB.
- `templates/index.html` contains the accessible page structure.
- `static/styles.css` holds the responsive Warm Ivory, Forest Green, and Terracotta design.
- `static/app.js` powers recipe search, quick categories, random inspiration, and recipe details.

The search box accepts a dish name or one ingredient. If no dish title matches, Golden Tavern tries that term as an ingredient. The API is free to explore and does not need a key.

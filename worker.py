"""Cloudflare Workers entry point for the Golden Tavern Flask app."""

from flask import Response, request
from pyodide.ffi import run_sync
from workers import wsgi

from app import app


def serve_asset(path: str) -> Response:
    """Read the page and its static files from the Cloudflare asset binding."""
    assets = request.environ["workers.env"].ASSETS
    asset_response = run_sync(assets.fetch(f"https://assets.local/{path}"))
    body = run_sync(asset_response.bytes())
    return Response(body, status=asset_response.status, headers=asset_response.headers)


def serve_home() -> Response:
    return serve_asset("index.html")


def serve_static(filename: str) -> Response:
    return serve_asset(f"static/{filename}")


# Replace Flask's local file handlers with Cloudflare's static asset binding.
app.view_functions["home"] = serve_home
app.view_functions["static"] = serve_static

Default = wsgi.entrypoint(app)

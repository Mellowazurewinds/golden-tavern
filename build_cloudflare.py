"""Prepare Golden Tavern's Flask template and static files for Cloudflare."""

from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parent
PUBLIC = ROOT / "public"

(PUBLIC / "static").mkdir(parents=True, exist_ok=True)
shutil.copy2(ROOT / "templates" / "index.html", PUBLIC / "index.html")
shutil.copytree(ROOT / "static", PUBLIC / "static", dirs_exist_ok=True)
print(f"Cloudflare site assets prepared in {PUBLIC}")

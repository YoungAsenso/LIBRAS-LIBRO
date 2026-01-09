import os
from pathlib import Path
from flask import Flask, send_from_directory, render_template_string, request

APP_DIR = Path(__file__).resolve().parent

# Prefer the new wider image, fallback to the old one
COVER_PATH = next(APP_DIR.glob("CRYSTOL ALBUM FULL.*"), None) or next(APP_DIR.glob("CRYSTOL ALBUM.*"), None)
COVER_NAME = COVER_PATH.name if COVER_PATH else None

TARGET_ISO = "2026-02-13T00:00:00"

app = Flask(__name__)
def home():
    if not COVER_NAME:
        return ("Missing cover image. Add CRYSTOL ALBUM FULL.* or CRYSTOL ALBUM.* to the repo root.", 500)
    return render_template_string(PAGE, target=TARGET_ISO)
@app.route("/cover")
def cover():
    return send_from_directory(APP_DIR, COVER_NAME)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)



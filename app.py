import os
from pathlib import Path
from urllib.parse import quote

from flask import Flask, abort, render_template_string, send_from_directory

APP_DIR = Path(__file__).resolve().parent
AUDIO_DIR = APP_DIR  # your WAVs are in repo root right now

app = Flask(__name__)

PAGE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>LIBRAS LIBRO — Player</title>
  <style>
    body { font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif; margin: 24px; }
    .wrap { max-width: 900px; margin: 0 auto; }
    h1 { margin: 0 0 8px; }
    .meta { opacity: .7; margin-bottom: 18px; }
    .row { display: flex; gap: 12px; align-items: center; padding: 10px 0; border-bottom: 1px solid #eee; }
    button { padding: 8px 10px; cursor: pointer; }
    .name { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    audio { width: 100%; margin-top: 14px; }
    .small { font-size: 12px; opacity: .7; margin-top: 10px; }
    input { width: 100%; padding: 10px; margin: 12px 0; }
  </style>
</head>
<body>
<div class="wrap">
  <h1>LIBRAS LIBRO</h1>
  <div class="meta">{{count}} tracks</div>

  <input id="filter" placeholder="Filter tracks…" oninput="filterList()" />

  <div id="list">
    {% for t in tracks %}
      <div class="row" data-name="{{t.display|lower}}">
        <button onclick="play('{{t.url}}','{{t.display|e}}')">Play</button>
        <div class="name" title="{{t.display}}">{{t.display}}</div>
      </div>
    {% endfor %}
  </div>

  <audio id="player" controls preload="none"></audio>
  <div id="now" class="small"></div>
</div>

<script>
  const player = document.getElementById("player");
  const now = document.getElementById("now");

  function play(url, name){
    player.src = url;
    player.play();
    now.textContent = "Now playing: " + name;
  }

  function filterList(){
    const q = document.getElementById("filter").value.trim().toLowerCase();
    document.querySelectorAll("#list .row").forEach(r => {
      const n = r.getAttribute("data-name") || "";
      r.style.display = n.includes(q) ? "" : "none";
    });
  }
</script>
</body>
</html>
"""

def list_wavs(folder: Path):
  files = sorted([p for p in folder.iterdir() if p.is_file() and p.suffix.lower() == ".wav"])
  tracks = []
  for p in files:
    # quote() is important because your filenames contain spaces
    tracks.append({
      "display": p.name,
      "url": f"/audio/{quote(p.name)}"
    })
  return tracks

@app.get("/")
def index():
  tracks = list_wavs(AUDIO_DIR)
  return render_template_string(PAGE, tracks=tracks, count=len(tracks))

@app.get("/audio/<path:filename>")
def audio(filename):
  file_path = AUDIO_DIR / filename
  if not file_path.exists() or not file_path.is_file() or file_path.suffix.lower() != ".wav":
    abort(404)

  # conditional=True enables caching headers; works well for media delivery
  return send_from_directory(AUDIO_DIR, filename, as_attachment=False, conditional=True)

if __name__ == "__main__":
  port = int(os.environ.get("PORT", "8080"))
  app.run(host="0.0.0.0", port=port)

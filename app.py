import os
from pathlib import Path
from urllib.parse import quote

from flask import Flask, abort, render_template_string, send_from_directory, request

APP_DIR = Path(__file__).resolve().parent

# Your repo layout: WAVs + cover in the repo root
AUDIO_DIR = APP_DIR
COVER_BASENAME = "CRYSTOL ALBUM"  # matches "CRYSTOL ALBUM.png"

app = Flask(__name__)

PAGE = r"""
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>LIBRAS LIBRO — Player</title>

  <style>
    :root{
      /* cover-inspired palette (deep reds + warm orange highlights) */
      --bg: #070505;
      --panel: rgba(255,255,255,.04);
      --panel2: rgba(255,255,255,.06);
      --stroke: rgba(255,255,255,.10);
      --text: rgba(255,255,255,.92);
      --muted: rgba(255,255,255,.62);

      --hot: #ff4a2d;
      --hot2: #ff7a2a;
      --danger: #b31212;
      --glow: rgba(255, 92, 40, .35);

      --radius: 18px;
    }

    * { box-sizing: border-box; }

    body{
      margin: 0;
      font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
      background: radial-gradient(1200px 600px at 50% -10%, rgba(255,80,40,.22), transparent 55%),
                  radial-gradient(900px 500px at 20% 10%, rgba(179,18,18,.18), transparent 55%),
                  var(--bg);
      color: var(--text);
    }

    .wrap{
      max-width: 980px;
      margin: 0 auto;
      padding: 22px 18px 40px;
    }

    .hero{
      display: grid;
      grid-template-columns: 260px 1fr;
      gap: 18px;
      align-items: end;
      padding: 18px;
      background: linear-gradient(180deg, rgba(255,255,255,.05), rgba(255,255,255,.02));
      border: 1px solid var(--stroke);
      border-radius: var(--radius);
      box-shadow: 0 20px 70px rgba(0,0,0,.45);
      position: relative;
      overflow: hidden;
    }

    .hero:before{
      content:"";
      position:absolute;
      inset:-40px;
      background: radial-gradient(600px 220px at 10% 10%, rgba(255,122,42,.20), transparent 60%),
                  radial-gradient(520px 240px at 90% 20%, rgba(179,18,18,.16), transparent 60%);
      filter: blur(10px);
      pointer-events:none;
    }

    .cover{
      width: 100%;
      aspect-ratio: 1 / 1;
      border-radius: 16px;
      border: 1px solid var(--stroke);
      background: rgba(255,255,255,.03);
      box-shadow: 0 18px 50px rgba(0,0,0,.55);
      object-fit: cover;
      position: relative;
      z-index: 1;
    }

    .meta{
      position: relative;
      z-index: 1;
      padding-bottom: 6px;
    }

    .title{
      font-size: 40px;
      letter-spacing: .5px;
      margin: 0 0 6px;
      line-height: 1.05;
    }

    .sub{
      margin: 0 0 14px;
      color: var(--muted);
      font-size: 14px;
    }

    .controls{
      display: flex;
      gap: 10px;
      align-items: center;
      flex-wrap: wrap;
    }

    input#filter{
      flex: 1;
      min-width: 240px;
      padding: 12px 12px;
      border-radius: 14px;
      border: 1px solid var(--stroke);
      background: rgba(0,0,0,.35);
      color: var(--text);
      outline: none;
    }
    input#filter::placeholder{ color: rgba(255,255,255,.40); }

    .pill{
      padding: 10px 12px;
      border-radius: 999px;
      border: 1px solid var(--stroke);
      background: rgba(255,255,255,.04);
      color: var(--muted);
      font-size: 13px;
      white-space: nowrap;
    }

    .list{
      margin-top: 16px;
      border-radius: var(--radius);
      border: 1px solid var(--stroke);
      overflow: hidden;
      background: rgba(255,255,255,.03);
    }

    .row{
      display: grid;
      grid-template-columns: 64px 1fr 90px;
      gap: 12px;
      align-items: center;
      padding: 12px 14px;
      border-bottom: 1px solid rgba(255,255,255,.06);
      background: rgba(0,0,0,.14);
      transition: transform .08s ease, background .15s ease;
    }
    .row:last-child{ border-bottom: none; }
    .row:hover{
      background: rgba(255,255,255,.04);
    }

    .row.playing{
      background: linear-gradient(90deg, rgba(255,74,45,.20), rgba(255,122,42,.08));
      box-shadow: inset 0 0 0 1px rgba(255,122,42,.25);
    }

    .btn{
      width: 52px;
      height: 40px;
      border-radius: 12px;
      border: 1px solid rgba(255,255,255,.12);
      background: rgba(255,255,255,.04);
      color: var(--text);
      cursor: pointer;
      display: grid;
      place-items: center;
      transition: transform .08s ease, border-color .15s ease, background .15s ease;
    }
    .btn:hover{
      transform: translateY(-1px);
      border-color: rgba(255,122,42,.40);
      background: rgba(255,122,42,.10);
      box-shadow: 0 0 0 6px rgba(255,122,42,.08);
    }
    .btn:active{ transform: translateY(0px); }

    .name{
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      font-size: 14px;
    }

    .tag{
      justify-self: end;
      font-size: 12px;
      color: rgba(255,255,255,.55);
      border: 1px solid rgba(255,255,255,.10);
      padding: 6px 10px;
      border-radius: 999px;
      background: rgba(0,0,0,.20);
    }

    .playerbar{
      margin-top: 14px;
      padding: 14px;
      border-radius: var(--radius);
      border: 1px solid var(--stroke);
      background: rgba(0,0,0,.25);
      box-shadow: 0 18px 60px rgba(0,0,0,.35);
    }

    audio{
      width: 100%;
      filter: drop-shadow(0 10px 30px rgba(0,0,0,.55));
    }

    .now{
      margin-top: 8px;
      font-size: 12px;
      color: rgba(255,255,255,.65);
    }

    @media (max-width: 760px){
      .hero{ grid-template-columns: 1fr; }
      .title{ font-size: 34px; }
      .row{ grid-template-columns: 64px 1fr; }
      .tag{ display: none; }
    }
  </style>
</head>

<body>
  <div class="wrap">
    <div class="hero">
      <img class="cover" src="/cover" alt="CRYSTOL ALBUM cover" onerror="this.style.display='none'">
      <div class="meta">
        <h1 class="title">LIBRAS LIBRO</h1>
        <p class="sub">{{ count }} tracks · streamed from Render</p>

        <div class="controls">
          <input id="filter" placeholder="Filter tracks…" oninput="filterList()">
          <div class="pill" id="status">Ready</div>
        </div>

        <div class="playerbar">
          <audio id="player" controls preload="none"></audio>
          <div class="now" id="now"></div>
        </div>
      </div>
    </div>

    <div class="list" id="list">
      {% for t in tracks %}
        <div class="row" data-name="{{t.display|lower}}" data-url="{{t.url}}" onclick="playFromRow(this)">
          <button class="btn" onclick="event.stopPropagation(); play('{{t.url}}','{{t.display|e}}', this.closest('.row'))">▶</button>
          <div class="name" title="{{t.display}}">{{t.display}}</div>
          <div class="tag">WAV</div>
        </div>
      {% endfor %}
    </div>
  </div>

<script>
  const player = document.getElementById("player");
  const now = document.getElementById("now");
  const statusPill = document.getElementById("status");

  let currentRow = null;

  function setPlayingRow(row){
    if(currentRow) currentRow.classList.remove("playing");
    currentRow = row;
    if(currentRow) currentRow.classList.add("playing");
  }

  function play(url, name, row=null){
    player.src = url;
    player.play();
    now.textContent = "Now playing: " + name;
    statusPill.textContent = "Playing";
    setPlayingRow(row);
  }

  function playFromRow(row){
    const url = row.getAttribute("data-url");
    const name = row.querySelector(".name")?.textContent || "Track";
    play(url, name, row);
  }

  function filterList(){
    const q = document.getElementById("filter").value.trim().toLowerCase();
    document.querySelectorAll("#list .row").forEach(r => {
      const n = r.getAttribute("data-name") || "";
      r.style.display = n.includes(q) ? "" : "none";
    });
  }

  player.addEventListener("pause", () => {
    if(player.currentTime > 0 && !player.ended) statusPill.textContent = "Paused";
  });

  player.addEventListener("ended", () => {
    statusPill.textContent = "Ended";
    // optional: auto-clear highlight
    // setPlayingRow(null);
  });

  player.addEventListener("error", () => {
    statusPill.textContent = "Error";
  });
</script>
</body>
</html>
"""

def find_cover_file() -> Path | None:
  # Try common extensions with and without exact match
  candidates = []
  for ext in (".png", ".jpg", ".jpeg", ".webp"):
    candidates.append(APP_DIR / f"{COVER_BASENAME}{ext}")
    candidates.append(APP_DIR / f"{COVER_BASENAME}{ext.upper()}")
  for p in candidates:
    if p.exists() and p.is_file():
      return p
  # Fallback: any file that starts with COVER_BASENAME and is an image
  for p in APP_DIR.iterdir():
    if p.is_file() and p.stem == COVER_BASENAME and p.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp"):
      return p
  return None

def list_wavs(folder: Path):
  files = sorted([p for p in folder.iterdir() if p.is_file() and p.suffix.lower() == ".wav"])
  tracks = []
  for p in files:
    tracks.append({
      "display": p.name,
      "url": f"/audio/{quote(p.name)}"  # handles spaces
    })
  return tracks

@app.get("/")
def index():
  tracks = list_wavs(AUDIO_DIR)
  return render_template_string(PAGE, tracks=tracks, count=len(tracks))

@app.get("/cover")
def cover():
  cover_file = find_cover_file()
  if not cover_file:
    abort(404)
  return send_from_directory(APP_DIR, cover_file.name, as_attachment=False, conditional=True)

@app.get("/audio/<path:filename>")
def audio(filename):
  file_path = AUDIO_DIR / filename
  if not file_path.exists() or not file_path.is_file() or file_path.suffix.lower() != ".wav":
    abort(404)
  return send_from_directory(AUDIO_DIR, filename, as_attachment=False, conditional=True)

if __name__ == "__main__":
  port = int(os.environ.get("PORT", "8080"))
  app.run(host="0.0.0.0", port=port)

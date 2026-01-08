import os
import re
import json
from pathlib import Path
from urllib.parse import quote

from flask import Flask, abort, render_template_string, send_from_directory

APP_DIR = Path(__file__).resolve().parent

# Repo layout: WAVs + cover in the repo root
AUDIO_DIR = APP_DIR
COVER_BASENAME = "CRYSTOL ALBUM"  # matches "CRYSTOL ALBUM.png"

app = Flask(__name__)

ALBUM_ORDER = [
    "Yulaf.wav",
    "Orange Royal.wav",
    "Saba Type Bitch.wav",
    "Load.wav",
    "Leyte Shutdown.wav",
    "To Purok Dos.wav",
    "Aurora Lights.wav",
    "Ijahay.wav",
    "Choyins.wav",
    "Tip Education.wav",
    "Puro Alibi.wav",
    "Kilim Horizon.wav",
    "Prosecco Rose Unja Tootsie.wav",
    "European Bugoy.wav",
    "Keep It Bongga.wav",
    "50K.wav",
    "Leopard Resort.wav",
    "Aksyonag.wav",
    "Ako Metros Bi.wav",
]

PAGE = r"""
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>LIBRAS LIBRO - Player</title>

  <style>
    :root{
      --bg: #070505;
      --panel: rgba(255,255,255,.04);
      --stroke: rgba(255,255,255,.10);
      --text: rgba(255,255,255,.92);
      --muted: rgba(255,255,255,.62);
      --hot: #ff4a2d;
      --hot2: #ff7a2a;
      --radius: 18px;
    }
    *{ box-sizing:border-box; }

    body{
      margin:0;
      font-family: system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif;
      background:
        radial-gradient(1200px 600px at 50% -10%, rgba(255,80,40,.22), transparent 55%),
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
      display:grid;
      grid-template-columns: 260px 1fr;
      gap: 18px;
      align-items:end;
      padding: 18px;
      background: linear-gradient(180deg, rgba(255,255,255,.05), rgba(255,255,255,.02));
      border: 1px solid var(--stroke);
      border-radius: var(--radius);
      box-shadow: 0 20px 70px rgba(0,0,0,.45);
      position:relative;
      overflow:hidden;
    }
    .hero:before{
      content:"";
      position:absolute;
      inset:-40px;
      background:
        radial-gradient(600px 220px at 10% 10%, rgba(255,122,42,.20), transparent 60%),
        radial-gradient(520px 240px at 90% 20%, rgba(179,18,18,.16), transparent 60%);
      filter: blur(10px);
      pointer-events:none;
    }

    .cover{
      width:100%;
      aspect-ratio:1/1;
      border-radius:16px;
      border:1px solid var(--stroke);
      background: rgba(255,255,255,.03);
      box-shadow: 0 18px 50px rgba(0,0,0,.55);
      object-fit:cover;
      position:relative;
      z-index:1;
    }

    .meta{
      position:relative;
      z-index:1;
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
      display:flex;
      gap: 10px;
      align-items:center;
      flex-wrap: wrap;
    }

    .pill{
      padding: 10px 12px;
      border-radius: 999px;
      border: 1px solid var(--stroke);
      background: rgba(255,255,255,.04);
      color: var(--muted);
      font-size: 13px;
      white-space: nowrap;
    }

    .iconbtn{
      width: 44px;
      height: 40px;
      border-radius: 999px;
      border: 1px solid rgba(255,255,255,.12);
      background: rgba(255,255,255,.04);
      color: var(--text);
      cursor: pointer;
      display: grid;
      place-items: center;
      transition: transform .08s ease, border-color .15s ease, background .15s ease;
      user-select:none;
    }
    .iconbtn:hover{
      transform: translateY(-1px);
      border-color: rgba(255,122,42,.40);
      background: rgba(255,122,42,.10);
      box-shadow: 0 0 0 6px rgba(255,122,42,.08);
    }
    .iconbtn:active{ transform: translateY(0px); }
    .iconbtn.on{
      border-color: rgba(255,122,42,.55);
      background: rgba(255,122,42,.14);
      box-shadow: 0 0 0 6px rgba(255,122,42,.06);
    }
    .iconbtn svg{ width: 18px; height: 18px; opacity: .92; }

    .playerbar{
      margin-top: 14px;
      padding: 14px;
      border-radius: var(--radius);
      border: 1px solid var(--stroke);
      background: rgba(0,0,0,.25);
      box-shadow: 0 18px 60px rgba(0,0,0,.35);
      position: relative;
    }

    .playerrow{
      display:flex;
      gap: 10px;
      align-items:center;
      margin-bottom: 10px;
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

    .list{
      margin-top: 16px;
      border-radius: var(--radius);
      border: 1px solid var(--stroke);
      overflow: hidden;
      background: rgba(255,255,255,.03);
    }

    .row{
      display:grid;
      grid-template-columns: 56px 64px 1fr;
      gap: 12px;
      align-items:center;
      padding: 12px 14px;
      border-bottom: 1px solid rgba(255,255,255,.06);
      background: rgba(0,0,0,.14);
      transition: background .15s ease;
      cursor: pointer;
    }
    .row:last-child{ border-bottom:none; }
    .row:hover{ background: rgba(255,255,255,.04); }

    .row.playing{
      background: linear-gradient(90deg, rgba(255,74,45,.20), rgba(255,122,42,.08));
      box-shadow: inset 0 0 0 1px rgba(255,122,42,.25);
    }

    .num{
      color: rgba(255,255,255,.45);
      font-size: 12px;
      letter-spacing: .2px;
      text-align: left;
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
      overflow:hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      font-size: 14px;
    }

    /* Fullscreen listening view */
    body.fs-on{
      background: radial-gradient(1200px 800px at 50% 10%, rgba(255,80,40,.18), transparent 60%), var(--bg);
    }
    body.fs-on .wrap{
      max-width: 1100px;
      padding: 18px 18px 28px;
    }
    body.fs-on .list{
      display:none;
    }
    body.fs-on .hero{
      grid-template-columns: 1fr;
      align-items:center;
      text-align:center;
      padding: 22px 18px;
    }
    body.fs-on .cover{
      max-width: 540px;
      margin: 0 auto;
    }
    body.fs-on .meta{
      padding-top: 12px;
    }
    body.fs-on .playerbar{
      max-width: 720px;
      margin: 14px auto 0;
    }
    body.fs-on .controls{
      justify-content: center;
    }

    @media (max-width: 760px){
      .hero{ grid-template-columns: 1fr; }
      .title{ font-size: 34px; }
      .row{ grid-template-columns: 46px 64px 1fr; }
    }
  </style>
</head>

<body>
  <div class="wrap">
    <div class="hero" id="hero">
      <img class="cover" id="coverImg" src="/cover" alt="CRYSTOL ALBUM cover" onerror="this.style.display='none'">
      <div class="meta">
        <h1 class="title">LIBRAS LIBRO</h1>
        <p class="sub">{{ count }} tracks</p>

        <div class="controls">
          <div class="pill" id="status">Ready</div>

          <!-- Repeat One -->
          <button class="iconbtn" id="repeatBtn" title="Repeat one">
            <!-- repeat-1 icon -->
            <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
              <path d="M7 7h9a4 4 0 0 1 4 4v2" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <path d="M17 3l-2 2 2 2" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M17 17H8a4 4 0 0 1-4-4v-2" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <path d="M7 21l2-2-2-2" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M12 10v6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <path d="M12 10h-1" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </button>

          <!-- Fullscreen -->
          <button class="iconbtn" id="fsBtn" title="Full screen">
            <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
              <path d="M8 3H5a2 2 0 0 0-2 2v3" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <path d="M16 3h3a2 2 0 0 1 2 2v3" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <path d="M8 21H5a2 2 0 0 1-2-2v-3" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <path d="M16 21h3a2 2 0 0 0 2-2v-3" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </button>
        </div>

        <div class="playerbar" id="playerbar">
          <audio id="player" controls preload="none"></audio>
          <div class="now" id="now"></div>
        </div>
      </div>
    </div>

    <div class="list" id="list">
      {% for t in tracks %}
        <div class="row" data-index="{{t.index}}" data-url="{{t.url}}" onclick="playFromRow(this)">
          <div class="num">{{"%02d"|format(t.index)}}</div>
          <button class="btn" onclick="event.stopPropagation(); playIndex({{t.index}});">&#9654;</button>
          <div class="name" title="{{t.display}}">{{t.display}}</div>
        </div>
      {% endfor %}
    </div>
  </div>

<script>
  const player = document.getElementById("player");
  const now = document.getElementById("now");
  const statusPill = document.getElementById("status");
  const repeatBtn = document.getElementById("repeatBtn");
  const fsBtn = document.getElementById("fsBtn");

  // Playlist (album order)
  const TRACKS = {{ tracks_json | safe }};
  let currentIndex = -1;
  let currentRow = null;

  function setPlayingRowByIndex(idx){
    if(currentRow) currentRow.classList.remove("playing");
    currentRow = document.querySelector(`.row[data-index="${idx}"]`);
    if(currentRow) currentRow.classList.add("playing");
  }

  function setNowPlaying(idx){
    const t = TRACKS.find(x => x.index === idx);
    if(!t) return;
    now.innerHTML = `Now playing: ${String(idx).padStart(2,"0")} &middot; ${t.display}`;
  }

  function playIndex(idx){
    const t = TRACKS.find(x => x.index === idx);
    if(!t) return;

    currentIndex = idx;
    player.src = t.url;
    player.play();
    statusPill.textContent = "Playing";
    setPlayingRowByIndex(idx);
    setNowPlaying(idx);
    // Repeat-one state should persist across tracks
    // (player.loop already reflects it)
  }

  function playFromRow(row){
    const idx = parseInt(row.getAttribute("data-index"), 10);
    playIndex(idx);
  }

  // Repeat one (single-track loop)
  function setRepeatOne(on){
    player.loop = !!on;
    repeatBtn.classList.toggle("on", !!on);
    repeatBtn.setAttribute("aria-pressed", on ? "true" : "false");
  }
  repeatBtn.addEventListener("click", () => {
    setRepeatOne(!player.loop);
    statusPill.textContent = player.paused ? "Ready" : (player.loop ? "Repeat" : "Playing");
  });
  setRepeatOne(false);

  // Autoplay next (album order), unless repeat-one is on (player.loop handles it)
  player.addEventListener("ended", () => {
    if(player.loop) return; // repeat-one will restart automatically
    const next = currentIndex + 1;
    const exists = TRACKS.some(t => t.index === next);
    if(exists){
      playIndex(next);
    }else{
      statusPill.textContent = "Ended";
    }
  });

  player.addEventListener("pause", () => {
    if(player.currentTime > 0 && !player.ended) statusPill.textContent = "Paused";
  });
  player.addEventListener("play", () => {
    statusPill.textContent = player.loop ? "Repeat" : "Playing";
  });
  player.addEventListener("error", () => { statusPill.textContent = "Error"; });

  // Full screen listening mode (true fullscreen when supported)
  function fsActive(){
    return !!document.fullscreenElement || document.body.classList.contains("fs-on");
  }

  async function enterFS(){
    document.body.classList.add("fs-on");
    try{
      // Request true fullscreen (best effort)
      await document.documentElement.requestFullscreen();
    }catch(e){
      // If browser blocks it, we still keep the "fs-on" layout
    }
    fsBtn.classList.add("on");
  }

  async function exitFS(){
    document.body.classList.remove("fs-on");
    try{
      if(document.fullscreenElement) await document.exitFullscreen();
    }catch(e){}
    fsBtn.classList.remove("on");
  }

  fsBtn.addEventListener("click", async () => {
    if(fsActive()) await exitFS();
    else await enterFS();
  });

  // Keep UI in sync if user exits fullscreen via ESC
  document.addEventListener("fullscreenchange", () => {
    const on = !!document.fullscreenElement;
    // If fullscreen exits, also exit our layout mode
    if(!on){
      document.body.classList.remove("fs-on");
      fsBtn.classList.remove("on");
    }else{
      document.body.classList.add("fs-on");
      fsBtn.classList.add("on");
    }
  });

  // Optional: start with first track loaded (not playing)
  // Uncomment if you want pre-selected track 01 without autoplay.
  // if(TRACKS.length){ currentIndex = TRACKS[0].index; player.src = TRACKS[0].url; setPlayingRowByIndex(currentIndex); setNowPlaying(currentIndex); }
</script>
</body>
</html>
"""

IMG_EXTS = {".png", ".jpg", ".jpeg", ".webp"}
WAV_EXT = ".wav"


def find_cover_file() -> Path | None:
    candidates = []
    for ext in (".png", ".jpg", ".jpeg", ".webp"):
        candidates.append(APP_DIR / f"{COVER_BASENAME}{ext}")
        candidates.append(APP_DIR / f"{COVER_BASENAME}{ext.upper()}")
    for p in candidates:
        if p.exists() and p.is_file():
            return p
    for p in APP_DIR.iterdir():
        if p.is_file() and p.stem == COVER_BASENAME and p.suffix.lower() in IMG_EXTS:
            return p
    return None


_num_re = re.compile(r"^\s*(\d{1,3})\s*[-._)]*\s*(.*)$")


def parse_track_number_and_title(filename: str):
    """
    Accepts:
      '01 Yulaf.wav', '1-Yulaf.wav', '1. Yulaf.wav', '1) Yulaf.wav'
    Falls back to no explicit number.
    """
    stem = Path(filename).stem  # removes .wav
    m = _num_re.match(stem)
    if m:
        n = int(m.group(1))
        title = (m.group(2) or "").strip()
        title = title if title else stem.strip()
        return n, title
    return None, stem.strip()


def list_wavs(folder: Path):
    # Map filename -> track number (1-based), based on ALBUM_ORDER
    order_num = {name.lower(): i + 1 for i, name in enumerate(ALBUM_ORDER)}

    files = [
        p for p in folder.iterdir()
        if p.is_file() and p.suffix.lower() == ".wav"
    ]

    # Sort:
    # 1) by ALBUM_ORDER track number (unknown ones go last)
    # 2) then by filename
    files.sort(
        key=lambda p: (
            order_num.get(p.name.lower(), 10**9),
            p.name.lower()
        )
    )

    tracks = []
    for p in files:
        idx = order_num.get(p.name.lower())
        display = Path(p.name).stem  # removes ".wav" in the UI
        tracks.append({
            "index": idx if idx is not None else (len(ALBUM_ORDER) + 1),
            "display": display,
            "url": f"/audio/{quote(p.name)}"
        })

    # If there are unknown tracks, give them unique increasing numbers at the end
    next_idx = len(ALBUM_ORDER) + 1
    for t in tracks:
        if t["index"] == len(ALBUM_ORDER) + 1:
            t["index"] = next_idx
            next_idx += 1

    return tracks


@app.route("/")
def index():
    tracks = list_wavs(AUDIO_DIR)
    tracks_json = json.dumps(tracks, ensure_ascii=False)

    return render_template_string(
        PAGE,
        tracks=tracks,
        tracks_json=tracks_json,
        count=len(tracks),
    )


@app.route("/audio/<path:filename>")
def audio(filename):
    p = AUDIO_DIR / filename
    if not p.exists() or not p.is_file():
        abort(404)
    return send_from_directory(AUDIO_DIR, filename)


@app.route("/cover")
def cover():
    p = find_cover_file()
    if not p:
        abort(404)
    return send_from_directory(APP_DIR, p.name)


if __name__ == "__main__":
    # Local dev only (Render uses start.sh / gunicorn)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=True)

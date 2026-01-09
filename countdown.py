import os
from pathlib import Path
from flask import Flask, send_from_directory, render_template_string, request

APP_DIR = Path(__file__).resolve().parent

# Prefer the new wider image, fallback to the old one
COVER_PATH = next(APP_DIR.glob("CRYSTOL ALBUM FULL.*"), None) or next(APP_DIR.glob("CRYSTOL ALBUM.*"), None)
COVER_NAME = COVER_PATH.name if COVER_PATH else None

TARGET_ISO = "2026-02-13T00:00:00"


PAGE = r"""
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>LIBRAS LIBRO Countdown</title>
  <style>
    html,body{height:100%;margin:0}
    body{background:#000;overflow:hidden;font-family:system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif}
    .frame{position:fixed;inset:0}
    .bg{position:absolute;inset:0;background:center/cover no-repeat}
    .fade{position:absolute;left:0;right:0;bottom:0;height:28vh;background:linear-gradient(to top, rgba(0,0,0,.75), rgba(0,0,0,0))}
    .overlay{position:absolute;left:0;right:0;bottom:4vh;display:flex;flex-direction:column;align-items:center;gap:10px;text-align:center}
    .nums{color:#fff;letter-spacing:.35em;font-weight:700;font-size:clamp(18px,4vw,44px);text-shadow:0 6px 30px rgba(0,0,0,.7)}
    .labels{color:rgba(255,255,255,.85);font-weight:600;letter-spacing:.25em;font-size:clamp(10px,1.6vw,14px)}
  </style>
</head>
<body>
  <div class="frame">
    <div class="bg" style="background-image:url('/cover');"></div>
    <div class="fade"></div>
    <div class="overlay">
      <div class="nums" id="nums">--   --   --   --</div>
      <div class="labels">DAYS&nbsp;&nbsp;HOURS&nbsp;&nbsp;MINS&nbsp;&nbsp;SECS</div>
    </div>
  </div>

<script>
  const TARGET = new Date("{{ target }}");
  const el = document.getElementById("nums");
  const pad2 = n => String(n).padStart(2,"0");

  function tick(){
    const now = new Date();
    let ms = TARGET - now;
    if(ms < 0) ms = 0;
    const total = Math.floor(ms/1000);
    const days = Math.floor(total/86400);
    const hours = Math.floor((total%86400)/3600);
    const mins = Math.floor((total%3600)/60);
    const secs = total%60;
    el.textContent = `${days}   ${pad2(hours)}   ${pad2(mins)}   ${pad2(secs)}`;
  }
  tick();
  setInterval(tick, 250);
</script>
</body>
</html>
"""
app = Flask(__name__)
@app.route("/")
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



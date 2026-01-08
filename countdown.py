import os
from pathlib import Path
from datetime import datetime
from flask import Flask, send_from_directory, render_template_string

APP_DIR = Path(__file__).resolve().parent
COVER_PATH = next(APP_DIR.glob("CRYSTOL ALBUM.*"), None)
COVER_NAME = COVER_PATH.name if COVER_PATH else None

TARGET_ISO = "2026-02-13T00:00:00"

app = Flask(__name__)

PAGE = """
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>LIBRAS LIBRO Countdown</title>
<style>
html,body{height:100%;margin:0;background:#000;font-family:system-ui,Segoe UI,Arial}
.wrap{height:100%;display:flex;align-items:center;justify-content:center}
.card{width:min(600px,92vw);aspect-ratio:1/1;position:relative;overflow:hidden}
.bg{position:absolute;inset:0;background:url("/cover") center/cover no-repeat}
.bar{position:absolute;left:0;right:0;bottom:0;height:72px;background:rgba(0,0,0,.88);
display:flex;flex-direction:column;align-items:center;justify-content:center;gap:6px}
.nums{font-family:Consolas,monospace;font-weight:800;color:#fff;font-size:26px;letter-spacing:.06em}
.labels{font-size:12px;color:rgba(255,255,255,.75);letter-spacing:.16em}
</style>
</head>
<body>
<div class="wrap">
  <div class="card">
    <div class="bg"></div>
    <div class="bar">
      <div class="nums" id="nums">--   --   --   --</div>
      <div class="labels">DAYS   HOURS   MINS   SECS</div>
    </div>
  </div>
</div>
<script>
const TARGET = new Date("{{ target }}");
const el = document.getElementById("nums");
function pad(n){return String(n).padStart(2,"0")}
function tick(){
  let t=Math.floor((TARGET-new Date())/1000); if(t<0)t=0;
  const d=Math.floor(t/86400); t%=86400;
  const h=Math.floor(t/3600); t%=3600;
  const m=Math.floor(t/60); const s=t%60;
  el.textContent=`${pad(d)}   ${pad(h)}   ${pad(m)}   ${pad(s)}`;
}
tick(); setInterval(tick,200);
</script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(PAGE, target=TARGET_ISO)

@app.route("/cover")
def cover():
    return send_from_directory(APP_DIR, COVER_NAME)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

import os
from pathlib import Path
from flask import Flask, send_from_directory, render_template_string

APP_DIR = Path(__file__).resolve().parent

# Prefer the new wider image, fallback to the old one
COVER_PATH = next(APP_DIR.glob("CRYSTOL ALBUM FULL.*"), None) or next(APP_DIR.glob("CRYSTOL ALBUM.*"), None)
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
  html, body { height:100%; margin:0; background:#000; overflow:hidden; }
  .wrap{
  position:fixed;
  inset:0;
}

  /* 1536x1024 = 3:2 so we lock aspect ratio */
  .card{
  position:fixed;
  inset:0;
  overflow:hidden;
}

  .bg{
  position:absolute;
  inset:0;
  background: url("/cover") center/cover no-repeat;
}

  /* Overlay text directly on image (no background fills) */
  .overlay{
  position:absolute;
  left:0;
  right:0;
  bottom:32px;
  display:flex;
  flex-direction:column;
  align-items:center;
  gap:8px;
  pointer-events:none;
}

  .nums{
    font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace;
    font-weight: 900;
    letter-spacing: .10em;
    color:#fff;
    font-size: clamp(20px, 3.0vw, 40px);
    line-height: 1;
    text-shadow: 0 4px 16px rgba(0,0,0,.95);
  }

  .labels{
    font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial;
    font-weight: 700;
    letter-spacing: .22em;
    color: rgba(255,255,255,.85);
    font-size: clamp(10px, 1.2vw, 14px);
    line-height: 1;
    text-shadow: 0 4px 14px rgba(0,0,0,.95);
  }

  /* Make it feel bigger on short screens */
  @media (max-height: 700px){
    .wrap{
  position:fixed;
  inset:0;
}
    .card{
  position:fixed;
  inset:0;
  overflow:hidden;
}
    .overlay{
  position:absolute;
  left:0;
  right:0;
  bottom:32px;
  display:flex;
  flex-direction:column;
  align-items:center;
  gap:8px;
  pointer-events:none;
}
  }
</style>
</head>
<body>
  <div class="wrap">
    <div class="card">
      <div class="bg"></div>
      <div class="overlay">
        <div class="nums" id="nums">--   --   --   --</div>
        <div class="labels">DAYS&nbsp;&nbsp;HOURS&nbsp;&nbsp;MINS&nbsp;&nbsp;SECS</div>
      </div>
    </div>
  </div>

<script>
  const TARGET = new Date("{{ target }}");
  const el = document.getElementById("nums");
  const pad2 = n => String(n).padStart(2,"0");

  function tick(){
    let t = Math.floor((TARGET - new Date()) / 1000);
    if (t < 0) t = 0;

    const d = Math.floor(t / 86400); t %= 86400;
    const h = Math.floor(t / 3600); t %= 3600;
    const m = Math.floor(t / 60);
    const s = t % 60;

    el.textContent = `${pad2(d)}   ${pad2(h)}   ${pad2(m)}   ${pad2(s)}`;
  }

  tick();
  setInterval(tick, 200);
</script>
</body>
</html>
"""

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


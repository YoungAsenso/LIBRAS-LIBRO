import os
from pathlib import Path
import psycopg2
from flask import Flask, send_from_directory, render_template_string, request

APP_DIR = Path(__file__).resolve().parent

# Prefer the new wider image, fallback to the old one
COVER_PATH = next(APP_DIR.glob("CRYSTOL ALBUM FULL.*"), None) or next(APP_DIR.glob("CRYSTOL ALBUM.*"), None)
COVER_NAME = COVER_PATH.name if COVER_PATH else None

TARGET_ISO = "2026-02-13T00:00:00"

app = Flask(__name__)

def get_db():
    # DATABASE_URL is set in Render Environment Variables
    return psycopg2.connect(os.environ["DATABASE_URL"])

def ensure_tables():
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS signups (
              id SERIAL PRIMARY KEY,
              username TEXT NOT NULL,
              email TEXT NOT NULL UNIQUE,
              created_at TIMESTAMP DEFAULT NOW()
            );
        """)
        conn.commit()
    finally:
        cur.close()
        conn.close()

# Create tables on startup (safe to run repeatedly)
try:
    ensure_tables()
except Exception as e:
    # Don't crash the whole site if DB is temporarily unavailable
    print("DB init error:", e)


def signup_enabled():
    return os.environ.get("SIGNUP_ENABLED", "false").lower() == "true"
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

.overlay::before{
  content:"";
  position:absolute;
  left:-20px;
  right:-20px;
  bottom:-14px;
  height:120px;
  background: linear-gradient(
    to top,
    rgba(0,0,0,0.55),
    rgba(0,0,0,0.25),
    rgba(0,0,0,0.0)
  );
  z-index:-1;
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

.overlay::before{
  content:"";
  position:absolute;
  left:-20px;
  right:-20px;
  bottom:-14px;
  height:120px;
  background: linear-gradient(
    to top,
    rgba(0,0,0,0.55),
    rgba(0,0,0,0.25),
    rgba(0,0,0,0.0)
  );
  z-index:-1;
  pointer-events:none;
}
  }
  /* Signup form (pointer-events enabled only for the form) */
  .signup {
    pointer-events: auto;
    display: flex;
    gap: 8px;
    margin-top: 10px;
    align-items: center;
    justify-content: center;
    flex-wrap: wrap;
  }

  .signup input {
    width: 180px;
    max-width: 44vw;
    background: rgba(0,0,0,0.55);
    border: 1px solid rgba(255,255,255,0.22);
    border-radius: 10px;
    color: #fff;
    padding: 10px 12px;
    font: 600 13px/1 system-ui, -apple-system, Segoe UI, Roboto, Arial;
    outline: none;
    box-shadow: 0 4px 16px rgba(0,0,0,.35);
  }

  .signup input::placeholder { color: rgba(255,255,255,0.65); }

  .signup button {
    pointer-events: auto;
    border: none;
    border-radius: 10px;
    padding: 10px 14px;
    font: 800 13px/1 system-ui, -apple-system, Segoe UI, Roboto, Arial;
    letter-spacing: .10em;
    cursor: pointer;
    background: #fff;
    color: #000;
    box-shadow: 0 8px 24px rgba(0,0,0,.45);
  }

  .signup small{
    width: 100%;
    text-align: center;
    color: rgba(255,255,255,0.75);
    font: 600 11px/1.2 system-ui, -apple-system, Segoe UI, Roboto, Arial;
    letter-spacing: .06em;
    text-shadow: 0 4px 14px rgba(0,0,0,.95);
    margin-top: 2px;
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
        {% if signup_enabled %}
<form class="signup" method="POST" action="/signup" autocomplete="on">
  <input name="username" placeholder="preferred username" required maxlength="32">
  <input name="email" type="email" placeholder="email" required maxlength="254">
  <button type="submit">ENTER</button>
  <small>Only used to verify your entry & contact winners. Not used for spam.</small>
</form>
{% endif %}
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
    return render_template_string(PAGE, target=TARGET_ISO, signup_enabled=signup_enabled())



@app.route("/signup", methods=["POST"])
def signup():
    if not signup_enabled():
        return ("Signups are currently closed.", 403)
    username = request.form.get("username", "").strip()
    email = request.form.get("email", "").strip().lower()

    if not username or not email:
        return ("Missing username or email.", 400)

    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO signups (username, email) VALUES (%s, %s)",
            (username, email)
        )
        conn.commit()
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        return ("This email is already entered.", 400)
    finally:
        cur.close()
        conn.close()

    return ("You're in.", 200)
@app.route("/cover")
def cover():
    return send_from_directory(APP_DIR, COVER_NAME)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)



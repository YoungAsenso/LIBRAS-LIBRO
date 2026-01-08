from tkinter import Tk, Canvas
from PIL import Image, ImageTk
from pathlib import Path
from datetime import datetime

WINDOW_SIZE = 600
TARGET = datetime(2026, 2, 13, 0, 0, 0)

BASE_DIR = Path(__file__).parent
img_path = next(BASE_DIR.glob("CRYSTOL ALBUM.*"))

root = Tk()
root.title("CRYSTOL ALBUM")
root.geometry(f"{WINDOW_SIZE}x{WINDOW_SIZE}")
root.configure(bg="black")

img = Image.open(img_path)
img.thumbnail((WINDOW_SIZE, WINDOW_SIZE), Image.LANCZOS)
photo = ImageTk.PhotoImage(img)

canvas = Canvas(root, width=WINDOW_SIZE, height=WINDOW_SIZE, highlightthickness=0)
canvas.pack(fill="both", expand=True)
canvas.create_image(WINDOW_SIZE//2, WINDOW_SIZE//2, image=photo)

# Bottom bar
canvas.create_rectangle(0, WINDOW_SIZE-70, WINDOW_SIZE, WINDOW_SIZE, fill="black", outline="")

# Numbers (bold, mono)
nums_text = canvas.create_text(
    WINDOW_SIZE//2, WINDOW_SIZE-44,
    fill="white",
    font=("Consolas", 26, "bold")
)

# Labels (lighter, smaller)
words_text = canvas.create_text(
    WINDOW_SIZE//2, WINDOW_SIZE-18,
    fill="#CFCFCF",
    font=("Segoe UI", 12)
)

def tick():
    now = datetime.now()
    total = int((TARGET - now).total_seconds())

    if total < 0:
        nums = "00   00   00   00"
    else:
        d = total // 86400
        r = total % 86400
        h = r // 3600
        r %= 3600
        m = r // 60
        s = r % 60
        nums = f"{d:02d}   {h:02d}   {m:02d}   {s:02d}"

    canvas.itemconfig(nums_text, text=nums)
    canvas.itemconfig(words_text, text="DAYS   HOURS   MINS   SECS")
    root.after(200, tick)

tick()
root.mainloop()


import math
import random
import subprocess
from PIL import Image, ImageDraw, ImageFont

W, H = 720, 1280
FPS = 24
DURATION = 18
TOTAL = FPS * DURATION

STORIES = [
    {
        "title": "NOOB VS PRO!",
        "captions": [
            "THE NOOB WAS LAUGHED AT...",
            "BUT HE HAD A SECRET!",
            "THE PRO NEVER SAW IT COMING!"
        ],
        "bg": (17, 34, 75),
        "accent": (255, 210, 40)
    },
    {
        "title": "LAVA IS RISING!",
        "captions": [
            "THE FLOOR STARTED SHAKING!",
            "EVERYONE RAN FOR SAFETY!",
            "ONE PLAYER FOUND A SECRET EXIT!"
        ],
        "bg": (70, 25, 35),
        "accent": (255, 100, 25)
    },
    {
        "title": "THE SECRET DOOR!",
        "captions": [
            "NOBODY COULD OPEN THIS DOOR...",
            "THEN A NOOB FOUND A KEY!",
            "WHAT WAS WAITING INSIDE?"
        ],
        "bg": (25, 30, 75),
        "accent": (70, 230, 255)
    }
]

def font(size):
    path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    return ImageFont.truetype(path, size)

def centered(draw, text, y, f, fill):
    box = draw.textbbox((0, 0), text, font=f, stroke_width=2)
    x = (W - (box[2] - box[0])) // 2
    draw.text((x, y), text, font=f, fill=fill,
              stroke_width=3, stroke_fill=(0, 0, 0))

def character(draw, x, y, shirt, jumping=False):
    y -= 35 if jumping else 0

    # Block-style head
    draw.rounded_rectangle(
        (x-32, y-105, x+32, y-41),
        radius=8, fill=(255, 195, 135),
        outline=(20, 20, 20), width=4
    )

    # Hair
    draw.rectangle(
        (x-32, y-110, x+32, y-95),
        fill=(45, 25, 15)
    )

    # Eyes
    draw.rectangle((x-19, y-80, x-9, y-70), fill="black")
    draw.rectangle((x+9, y-80, x+19, y-70), fill="black")

    # Body
    draw.rounded_rectangle(
        (x-39, y-41, x+39, y+42),
        radius=8, fill=shirt,
        outline=(15, 15, 15), width=4
    )

    # Arms
    draw.rectangle((x-58, y-35, x-39, y+28), fill=shirt)
    draw.rectangle((x+39, y-35, x+58, y+28), fill=shirt)

    # Legs
    draw.rectangle((x-34, y+42, x-7, y+105), fill=(35, 45, 75))
    draw.rectangle((x+7, y+42, x+34, y+105), fill=(35, 45, 75))

def make_frame(story, frame):
    img = Image.new("RGB", (W, H), story["bg"])
    d = ImageDraw.Draw(img)

    progress = frame / TOTAL
    t = frame / FPS

    # Background stars and buildings
    for i in range(12):
        bx = (i * 83) % W
        bh = 150 + (i * 47) % 260
        d.rectangle(
            (bx, 700-bh, bx+55, 700),
            fill=(30, 42, 80)
        )

    for i in range(24):
        sx = (i * 127) % W
        sy = (i * 193) % 650
        d.ellipse((sx, sy, sx+4, sy+4), fill=(210, 225, 255))

    # Ground
    d.rectangle((0, 700, W, H), fill=(35, 48, 65))
    d.rectangle((0, 700, W, 716), fill=story["accent"])

    # Animated obstacle
    obstacle_x = int(360 + math.sin(t * 2) * 170)
    d.rectangle(
        (obstacle_x-55, 620, obstacle_x+55, 700),
        fill=story["accent"]
    )

    # Characters move toward the obstacle
    hero_x = int(100 + progress * 430)
    rival_x = int(560 - progress * 280)

    jump = int(t * 3) % 2 == 0 and t > 7

    character(d, hero_x, 850, (35, 170, 255), jump)
    character(d, rival_x, 850, (255, 65, 80), False)

    # Title
    centered(d, "SHARKX SHADOWS", 65, font(30), (255, 255, 255))

    # Story title
    centered(d, story["title"], 190, font(48), story["accent"])

    # Changing captions
    section = min(2, int(progress * 3))
    caption = story["captions"][section]
    centered(d, caption, 1010, font(27), (255, 255, 255))

    # Animated progress bar
    d.rounded_rectangle(
        (65, 1150, 655, 1168),
        radius=8, fill=(75, 75, 90)
    )
    d.rounded_rectangle(
        (65, 1150, 65 + int(590*progress), 1168),
        radius=8, fill=story["accent"]
    )

    # Final call to action
    if progress > 0.88:
        centered(d, "WHAT HAPPENS NEXT?", 1200, font(27),
                 (255, 240, 80))

    return img

def create_video():
    story = random.choice(STORIES)

    command = [
        "ffmpeg", "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-pix_fmt", "rgb24",
        "-s", f"{W}x{H}",
        "-r", str(FPS),
        "-i", "-",
        "-an",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        "short.mp4"
    ]

    process = subprocess.Popen(command, stdin=subprocess.PIPE)

    try:
        for frame in range(TOTAL):
            img = make_frame(story, frame)
            process.stdin.write(img.tobytes())
        process.stdin.close()

        if process.wait() != 0:
            raise RuntimeError("FFmpeg video rendering failed")

    except Exception:
        process.kill()
        raise

    print("Video created successfully: short.mp4")
    print("Story:", story["title"])

if __name__ == "__main__":
    create_video()

import subprocess

def create_video():
    print("Starting video generation...")

    subprocess.run([
        "ffmpeg",
        "-y",
        "-f", "lavfi",
        "-i", "color=c=blue:s=1080x1920:d=30",
        "-vf",
        "drawtext=text='ROBLOX CHALLENGE':fontcolor=white:fontsize=65:x=(w-text_w)/2:y=h/2",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "short.mp4"
    ], check=True)

    print("Video created: short.mp4")

if __name__ == "__main__":
    create_video()

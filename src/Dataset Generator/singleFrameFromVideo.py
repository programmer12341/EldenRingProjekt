import subprocess
from pathlib import Path

# Nur diese Werte pro Durchlauf anpassen.
input_video = "e1.mp4"
timestamp = "00:00:10"
output_image = "preview_frame.jpg"

script_folder = Path(__file__).resolve().parent
project_root = Path(__file__).resolve().parents[2]

input_video_path = project_root / "data" / "videodaten" / input_video
output_image_path = script_folder / output_image

subprocess.run([
    "ffmpeg",
    "-y",
    "-ss", timestamp,
    "-i", str(input_video_path),
    "-frames:v", "1",
    str(output_image_path),
])

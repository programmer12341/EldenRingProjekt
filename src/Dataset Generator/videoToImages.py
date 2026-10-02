import subprocess
from pathlib import Path

input_video = "e1.mp4"
output_folder = "e1"

project_root = Path(__file__).resolve().parents[2]
video_folder = project_root / "data" / "videodaten"
image_collections_folder = project_root / "data" / "imageCollections"

input_video_path = video_folder / input_video
output_folder_path = image_collections_folder / output_folder
output_folder_path.mkdir(parents=True, exist_ok=True)

output_pattern = output_folder_path / "frame_%06d.jpg"

subprocess.run([
    "ffmpeg",
    "-i", str(input_video_path),
    "-vf", "fps=8,crop=1080:1080:420:0,format=rgb24",
    str(output_pattern)
])

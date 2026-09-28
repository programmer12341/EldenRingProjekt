import os
import subprocess

input_video = "Rohdaten_Cropped.mp4"
output_folder = "dataset"

os.makedirs(output_folder, exist_ok=True)

output_pattern = os.path.join(output_folder, "frame_%06d.jpg")

subprocess.run([
    "ffmpeg",
    "-i", input_video,
    "-t", "300",
    "-vf", "fps=8,scale=600:515,format=gray",
    output_pattern
])
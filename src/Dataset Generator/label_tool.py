import shutil
from pathlib import Path

import cv2

# Nur diese beiden Werte pro Label-Durchlauf anpassen.
input_collection = "e1"
output_collection = "e1_base_not_base"

project_root = Path(__file__).resolve().parents[2]

# Eingabe: bereits extrahierte Frames.
input_folder = project_root / "data" / "imageCollections" / input_collection

# Ausgabe: gelabelte Kopien der Frames.
output_root = project_root / "data" / "labelCollection" / output_collection
base_folder = output_root / "Base"
not_base_folder = output_root / "Not_Base"

base_folder.mkdir(parents=True, exist_ok=True)
not_base_folder.mkdir(parents=True, exist_ok=True)

image_extensions = {".jpg", ".jpeg", ".png"}

if not input_folder.exists():
    print(f"Eingabeordner nicht gefunden: {input_folder}")
    exit()

images = sorted([
    path for path in input_folder.iterdir()
    if path.suffix.lower() in image_extensions
])

if not images:
    print(f"Keine Bilder gefunden in: {input_folder}")
    exit()

cv2.namedWindow("Label Tool", cv2.WINDOW_NORMAL)

total = len(images)

for index, image_path in enumerate(images, start=1):
    image = cv2.imread(str(image_path))

    if image is None:
        print(f"Konnte Bild nicht laden: {image_path.name}")
        continue

    display = image.copy()

    progress_text = f"Bild {index} / {total}"
    cv2.putText(
        display,
        progress_text,
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (255, 255, 255),
        2,
    )

    cv2.putText(
        display,
        image_path.name,
        (10, 65),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2,
    )

    help_text = "B = Base   N = Not_Base   S = skip   Q / ESC = quit"
    height = display.shape[0]
    cv2.putText(
        display,
        help_text,
        (10, height - 20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2,
    )

    cv2.imshow("Label Tool", display)

    key = cv2.waitKey(0) & 0xFF

    if key == ord("b"):
        target = base_folder / image_path.name
        shutil.copy2(image_path, target)
        print(f"[BASE]     {image_path.name}")

    elif key == ord("n"):
        target = not_base_folder / image_path.name
        shutil.copy2(image_path, target)
        print(f"[NOT_BASE] {image_path.name}")

    elif key == ord("s"):
        print(f"[SKIP]     {image_path.name}")

    elif key == ord("q") or key == 27:
        print("Beendet.")
        break

cv2.destroyAllWindows()

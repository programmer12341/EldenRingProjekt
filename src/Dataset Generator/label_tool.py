import shutil
from pathlib import Path
import cv2

# Eingabeordner mit den extrahierten Frames
input_folder = Path("dataset")

# Ausgabeordner
output_root = Path("labeled")
attack_folder = output_root / "attack"
no_attack_folder = output_root / "no_attack"
skip_folder = output_root / "skip"

attack_folder.mkdir(parents=True, exist_ok=True)
no_attack_folder.mkdir(parents=True, exist_ok=True)
skip_folder.mkdir(parents=True, exist_ok=True)

# Alle Bilder laden
image_extensions = {".jpg", ".jpeg", ".png"}
images = sorted([p for p in input_folder.iterdir() if p.suffix.lower() in image_extensions])

if not images:
    print("Keine Bilder im dataset-Ordner gefunden.")
    exit()

cv2.namedWindow("Label Tool", cv2.WINDOW_NORMAL)

total = len(images)

for i, image_path in enumerate(images, start=1):
    img = cv2.imread(str(image_path))

    if img is None:
        print(f"Konnte Bild nicht laden: {image_path.name}")
        continue

    display = img.copy()

    # Obere Zeile: Fortschritt
    progress_text = f"Bild {i} / {total}"
    cv2.putText(display, progress_text, (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)

    # Zweite Zeile: Dateiname
    filename_text = image_path.name
    cv2.putText(display, filename_text, (10, 65),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    # Tastenhilfe unten
    help_text = "A = attack   N = no_attack   S = skip   Q / ESC = quit"
    h = display.shape[0]
    cv2.putText(display, help_text, (10, h - 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    cv2.imshow("Label Tool", display)

    key = cv2.waitKey(0) & 0xFF

    if key == ord("a"):
        target = attack_folder / image_path.name
        shutil.move(str(image_path), str(target))
        print(f"[ATTACK]    {image_path.name}")

    elif key == ord("n"):
        target = no_attack_folder / image_path.name
        shutil.move(str(image_path), str(target))
        print(f"[NO_ATTACK] {image_path.name}")

    elif key == ord("s"):
        target = skip_folder / image_path.name
        shutil.move(str(image_path), str(target))
        print(f"[SKIP]      {image_path.name}")

    elif key == ord("q") or key == 27:  # 27 = ESC
        print("Beendet.")
        break

cv2.destroyAllWindows()
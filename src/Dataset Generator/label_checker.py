import json
import random
import shutil
from pathlib import Path

import cv2

# Nur diesen Wert pro Check-Durchlauf anpassen.
label_collection = "e1_base_not_base"

project_root = Path(__file__).resolve().parents[2]
label_root = project_root / "data" / "labelCollection" / label_collection
progress_file = label_root / "checker_progress.json"

classes = {
    "Base": label_root / "Base",
    "Not_Base": label_root / "Not_Base",
}
uncertain_folder = label_root / "uncertain"
uncertain_folder.mkdir(parents=True, exist_ok=True)

image_extensions = {".jpg", ".jpeg", ".png"}


def load_progress():
    if not progress_file.exists():
        return set()

    with progress_file.open("r", encoding="utf-8") as file:
        progress = json.load(file)

    return set(progress.get("checked_images", []))


def save_progress(checked_images):
    progress = {
        "checked_images": sorted(checked_images),
    }

    with progress_file.open("w", encoding="utf-8") as file:
        json.dump(progress, file, indent=2)


samples = []

for label, folder in classes.items():
    if not folder.exists():
        print(f"Label-Ordner nicht gefunden: {folder}")
        exit()

    for image_path in folder.iterdir():
        if image_path.suffix.lower() in image_extensions:
            relative_path = image_path.relative_to(label_root).as_posix()
            samples.append((image_path, label, relative_path))

if not samples:
    print(f"Keine Bilder gefunden in: {label_root}")
    exit()

checked_images = load_progress()
remaining_samples = [
    sample for sample in samples
    if sample[2] not in checked_images
]
random.shuffle(remaining_samples)

total = len(samples)
already_checked = total - len(remaining_samples)

if not remaining_samples:
    print(f"Alle Bilder wurden bereits geprüft: {total} / {total}")
    exit()

print(f"Fortschritt geladen: {already_checked} / {total} bereits geprüft.")
print("B = Base | N = Not_Base | Q / ESC = pausieren")

cv2.namedWindow("Label Checker", cv2.WINDOW_NORMAL)

correct = 0
wrong = 0

for image_path, true_label, relative_path in remaining_samples:
    image = cv2.imread(str(image_path))

    if image is None:
        print(f"Konnte Bild nicht laden: {image_path.name}")
        checked_images.add(relative_path)
        save_progress(checked_images)
        continue

    while True:
        checked_count = len(checked_images)
        current_number = checked_count + 1
        progress_percent = checked_count / total * 100

        display = image.copy()

        cv2.putText(
            display,
            f"Fortschritt: {checked_count} / {total} ({progress_percent:.1f}%)",
            (10, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2,
        )

        cv2.putText(
            display,
            f"Aktuelles Bild: {current_number} / {total}",
            (10, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )

        cv2.putText(
            display,
            image_path.name,
            (10, 105),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2,
        )

        help_text = "B = Base   N = Not_Base   Q / ESC = pausieren"
        height = display.shape[0]
        cv2.putText(
            display,
            help_text,
            (10, height - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )

        cv2.imshow("Label Checker", display)
        key = cv2.waitKey(0) & 0xFF

        if key == ord("b"):
            user_label = "Base"
            break

        if key == ord("n"):
            user_label = "Not_Base"
            break

        if key == ord("q") or key == 27:
            save_progress(checked_images)
            print(f"Pausiert bei {checked_count} / {total} geprüften Bildern.")
            print(f"Diese Sitzung: {correct} richtig, {wrong} falsch.")
            cv2.destroyAllWindows()
            exit()

    if user_label == true_label:
        correct += 1
        result_text = "RICHTIG"
    else:
        wrong += 1
        result_text = "FALSCH"
        shutil.copy2(image_path, uncertain_folder / image_path.name)

    checked_images.add(relative_path)
    save_progress(checked_images)

    checked_count = len(checked_images)
    progress_percent = checked_count / total * 100
    print(
        f"[{result_text}] {relative_path} | "
        f"dein Label: {user_label} | altes Label: {true_label} | "
        f"Fortschritt: {checked_count} / {total} ({progress_percent:.1f}%)"
    )

print(f"Fertig. Alle Bilder geprüft: {total} / {total}")
print(f"Diese Sitzung: {correct} richtig, {wrong} falsch.")
cv2.destroyAllWindows()

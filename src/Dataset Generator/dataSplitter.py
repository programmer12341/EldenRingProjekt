import json
import random
import shutil
from pathlib import Path


# Nur diese Werte pro Dataset-Durchlauf anpassen.
label_collection = "e1_base_not_base"
samples_per_class = 632
random_seed = 42

train_ratio = 0.80
val_ratio = 0.10

# Wird nie als Klasse gezählt oder kopiert.
ignored_folders = {"uncertain"}

# None erzeugt automatisch z. B. e1_base_not_base_633_per_class_seed42
output_collection = None

# Aus Sicherheitsgründen nicht automatisch alte Datensätze überschreiben.
overwrite_output = False


project_root = Path(__file__).resolve().parents[2]
source_root = project_root / "data" / "labelCollection" / label_collection

if output_collection is None:
    output_collection = f"{label_collection}_{samples_per_class}_per_class_seed{random_seed}"

target_root = project_root / "data" / "finishedSetCollection" / output_collection

image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
test_ratio = 1.0 - train_ratio - val_ratio


def get_class_folders():
    if not source_root.exists():
        raise FileNotFoundError(f"LabelCollection nicht gefunden: {source_root}")

    class_folders = []
    for folder in sorted(source_root.iterdir()):
        if not folder.is_dir():
            continue
        if folder.name in ignored_folders:
            continue
        class_folders.append(folder)

    if not class_folders:
        raise RuntimeError(f"Keine Klassenordner gefunden in: {source_root}")

    return class_folders


def get_images(folder):
    return sorted(
        image_path
        for image_path in folder.iterdir()
        if image_path.is_file() and image_path.suffix.lower() in image_extensions
    )


def split_images(images):
    train_end = int(len(images) * train_ratio)
    val_end = int(len(images) * (train_ratio + val_ratio))

    return {
        "train": images[:train_end],
        "val": images[train_end:val_end],
        "test": images[val_end:],
    }


def prepare_output_folder():
    if target_root.exists() and any(target_root.iterdir()):
        if not overwrite_output:
            raise FileExistsError(
                f"Ausgabeordner existiert bereits und ist nicht leer: {target_root}\n"
                "Setze overwrite_output = True oder nutze einen anderen output_collection Namen."
            )
        shutil.rmtree(target_root)

    target_root.mkdir(parents=True, exist_ok=True)


def copy_split(split_name, class_name, images):
    output_folder = target_root / split_name / class_name
    output_folder.mkdir(parents=True, exist_ok=True)

    for image_path in images:
        shutil.copy2(image_path, output_folder / image_path.name)


def write_metadata(metadata):
    metadata_path = target_root / "metadata.json"
    with metadata_path.open("w", encoding="utf-8") as file:
        json.dump(metadata, file, indent=2)


def main():
    if train_ratio + val_ratio >= 1.0:
        raise ValueError("train_ratio + val_ratio muss kleiner als 1.0 sein.")

    random_generator = random.Random(random_seed)
    class_folders = get_class_folders()
    prepare_output_folder()

    metadata = {
        "source_label_collection": label_collection,
        "source_root": str(source_root),
        "output_collection": output_collection,
        "target_root": str(target_root),
        "samples_per_class": samples_per_class,
        "random_seed": random_seed,
        "split_ratios": {
            "train": train_ratio,
            "val": val_ratio,
            "test": test_ratio,
        },
        "ignored_folders": sorted(ignored_folders),
        "classes": {},
    }

    print(f"Quelle: {source_root}")
    print(f"Ziel:   {target_root}")
    print(f"Ignoriert: {', '.join(sorted(ignored_folders))}")
    print()

    for class_folder in class_folders:
        class_name = class_folder.name
        all_images = get_images(class_folder)

        if len(all_images) < samples_per_class:
            raise ValueError(
                f"{class_name} hat nur {len(all_images)} Bilder, "
                f"angefordert wurden aber {samples_per_class}."
            )

        selected_images = random_generator.sample(all_images, samples_per_class)
        selected_images = sorted(selected_images)
        splits = split_images(selected_images)

        metadata["classes"][class_name] = {
            "available_images": len(all_images),
            "selected_images": len(selected_images),
            "splits": {split_name: len(images) for split_name, images in splits.items()},
            "selected_files": [image_path.name for image_path in selected_images],
        }

        for split_name, split_images_for_class in splits.items():
            copy_split(split_name, class_name, split_images_for_class)

        print(
            f"{class_name}: {len(all_images)} vorhanden -> "
            f"{len(selected_images)} genutzt | "
            f"train {len(splits['train'])}, "
            f"val {len(splits['val'])}, "
            f"test {len(splits['test'])}"
        )

    write_metadata(metadata)
    print()
    print("Fertig.")


if __name__ == "__main__":
    main()

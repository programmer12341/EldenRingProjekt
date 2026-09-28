from pathlib import Path
import shutil

source_root = Path("labeled")
target_root = Path("dataset_final")

train_ratio = 0.70
val_ratio = 0.15

classes = ["attack", "no_attack"]

for class_name in classes:
    source_folder = source_root / class_name

    images = sorted(source_folder.glob("*.jpg"))

    total = len(images)

    train_end = int(total * train_ratio)
    val_end = int(total * (train_ratio + val_ratio))

    splits = {
        "train": images[:train_end],
        "val": images[train_end:val_end],
        "test": images[val_end:]
    }

    for split_name, split_images in splits.items():
        output_folder = target_root / split_name / class_name
        output_folder.mkdir(parents=True, exist_ok=True)

        for image_path in split_images:
            shutil.copy2(image_path, output_folder / image_path.name)

        print(
            f"{class_name} -> {split_name}: "
            f"{len(split_images)} Bilder"
        )
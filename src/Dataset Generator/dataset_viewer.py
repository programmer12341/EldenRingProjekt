import argparse
import json
import random
from pathlib import Path

import cv2
import numpy as np


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
MARKS_FILENAME = "dataset_viewer_marks.json"

# Nur diese Werte bei Bedarf anpassen.
dataset_folder = "data/labelCollection/e1_base_not_base"
grid_rows = 4
grid_columns = 6
random_sample_size = 50

project_root = Path(__file__).resolve().parents[2]


class DatasetViewer:
    def __init__(self, dataset_path, rows=4, columns=6, sample_size=50):
        self.dataset_path = Path(dataset_path).expanduser().resolve()
        self.rows = rows
        self.columns = columns
        self.sample_size = sample_size

        self.window_name = "Dataset Viewer"
        self.preview_window_name = "Preview"
        self.mode = "all"
        self.seed = None
        self.class_index = 0
        self.page_index = 0
        self.selected_index = 0

        self.class_to_images = {}
        self.class_names = []
        self.visible_images = []
        self.marks = set()
        self.tile_rects = []

        self.header_height = 150
        self.footer_height = 48
        self.tile_width = 190
        self.tile_height = 160
        self.label_height = 32

    def run(self):
        self.load_dataset()
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(
            self.window_name,
            self.columns * self.tile_width,
            self.header_height + self.rows * self.tile_height + self.footer_height,
        )
        cv2.setMouseCallback(self.window_name, self.on_mouse)

        self.apply_filters(reset_sample=True)

        while True:
            canvas = self.render()
            cv2.imshow(self.window_name, canvas)
            key = cv2.waitKey(0) & 0xFF

            if key in (ord("q"), 27):
                break
            if key in (ord("a"), ord("A")):
                self.mode = "all"
                self.apply_filters(reset_sample=False)
            elif key in (ord("s"), ord("S")):
                self.mode = "sample"
                self.apply_filters(reset_sample=True)
            elif key in (ord("r"), ord("R")):
                self.mode = "sample"
                self.apply_filters(reset_sample=True)
            elif key in (ord("m"), ord("M")):
                self.toggle_mark()
            elif key in (ord("+"), ord("=")):
                self.sample_size += 10
                self.apply_filters(reset_sample=False)
            elif key in (ord("-"), ord("_")):
                self.sample_size = max(1, self.sample_size - 10)
                self.apply_filters(reset_sample=False)
            elif key in (ord("n"), ord("N"), 83):
                self.next_page()
            elif key in (ord("p"), ord("P"), 81):
                self.previous_page()
            elif key in (82, ord("w"), ord("W")):
                self.change_class(-1)
            elif key in (84, ord("d"), ord("D")):
                self.change_class(1)
            elif key in (13, 32):
                self.open_preview()
            elif key == ord("1"):
                self.select_class_by_number(0)
            elif key == ord("2"):
                self.select_class_by_number(1)
            elif key == ord("3"):
                self.select_class_by_number(2)
            elif key == ord("4"):
                self.select_class_by_number(3)
            elif key == ord("5"):
                self.select_class_by_number(4)
            elif key == ord("6"):
                self.select_class_by_number(5)
            elif key == ord("7"):
                self.select_class_by_number(6)
            elif key == ord("8"):
                self.select_class_by_number(7)
            elif key == ord("9"):
                self.select_class_by_number(8)

        cv2.destroyAllWindows()

    def load_dataset(self):
        if not self.dataset_path.exists() or not self.dataset_path.is_dir():
            raise FileNotFoundError(f"Dataset folder not found: {self.dataset_path}")

        self.class_to_images = {}
        for child in sorted(self.dataset_path.iterdir()):
            if not child.is_dir():
                continue

            images = sorted(
                image_path
                for image_path in child.iterdir()
                if image_path.is_file() and image_path.suffix.lower() in IMAGE_EXTENSIONS
            )
            if images:
                self.class_to_images[child.name] = images

        if not self.class_to_images:
            raise RuntimeError(f"No image class folders found in: {self.dataset_path}")

        self.class_names = ["ALL"] + sorted(self.class_to_images)
        self.load_marks()

    def load_marks(self):
        marks_path = self.dataset_path / MARKS_FILENAME
        if not marks_path.exists():
            self.marks = set()
            return

        try:
            with marks_path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except (OSError, json.JSONDecodeError):
            self.marks = set()
            return

        self.marks = set(data.get("marked_images", []))

    def save_marks(self):
        marks_path = self.dataset_path / MARKS_FILENAME
        with marks_path.open("w", encoding="utf-8") as file:
            json.dump({"marked_images": sorted(self.marks)}, file, indent=2)

    def apply_filters(self, reset_sample):
        if reset_sample or self.seed is None:
            self.seed = random.randint(1, 999999)

        selected_class = self.class_names[self.class_index]
        if self.mode == "sample":
            self.visible_images = self.build_sample(selected_class)
        else:
            self.visible_images = self.collect_images(selected_class)

        self.page_index = 0
        self.selected_index = 0

    def collect_images(self, selected_class):
        if selected_class == "ALL":
            images = []
            for class_name in sorted(self.class_to_images):
                images.extend((class_name, image_path) for image_path in self.class_to_images[class_name])
            return images

        return [(selected_class, image_path) for image_path in self.class_to_images[selected_class]]

    def build_sample(self, selected_class):
        rng = random.Random(self.seed)
        if selected_class == "ALL":
            sample = []
            for class_name in sorted(self.class_to_images):
                images = list(self.class_to_images[class_name])
                take = min(self.sample_size, len(images))
                sample.extend((class_name, image_path) for image_path in rng.sample(images, take))
            rng.shuffle(sample)
            return sample

        images = list(self.class_to_images[selected_class])
        take = min(self.sample_size, len(images))
        return [(selected_class, image_path) for image_path in rng.sample(images, take)]

    def render(self):
        width = self.columns * self.tile_width
        height = self.header_height + self.rows * self.tile_height + self.footer_height
        canvas = np.full((height, width, 3), 245, dtype=np.uint8)

        self.draw_header(canvas)
        self.draw_grid(canvas)
        self.draw_footer(canvas)

        return canvas

    def draw_header(self, canvas):
        width = canvas.shape[1]
        cv2.rectangle(canvas, (0, 0), (width, self.header_height), (35, 35, 35), -1)

        selected_class = self.class_names[self.class_index]
        total = sum(len(images) for images in self.class_to_images.values())
        visible = len(self.visible_images)
        marked_visible = sum(1 for _class_name, path in self.visible_images if self.relative_key(path) in self.marks)

        title = f"Dataset: {self.dataset_path}"
        state = (
            f"Folder: {selected_class} | Mode: {self.mode.upper()} | "
            f"Showing: {visible} / {total} | Marked in view: {marked_visible} | "
            f"Sample/class: {self.sample_size} | Seed: {self.seed}"
        )
        controls = (
            "Q quit | A all images | S sample | R new sample | W/D folder | "
            "N/P page | Enter/Space preview | M mark | +/- sample size | 1-9 folder"
        )

        self.put_text(canvas, title, 12, 28, scale=0.62, color=(255, 255, 255), thickness=2)
        self.put_text(canvas, state, 12, 58, scale=0.62, color=(210, 245, 255), thickness=2)
        self.put_text(canvas, controls, 12, 88, scale=0.5, color=(230, 230, 230), thickness=1)

        x = 12
        y = 123
        for index, class_name in enumerate(self.class_names):
            if class_name == "ALL":
                count = total
                percent = 100.0
            else:
                count = len(self.class_to_images[class_name])
                percent = count / total * 100 if total else 0.0

            text = f"{index + 1}:{class_name} {count} ({percent:.1f}%)"
            color = (110, 230, 110) if index == self.class_index else (235, 235, 235)
            self.put_text(canvas, text, x, y, scale=0.48, color=color, thickness=1)
            x += max(155, len(text) * 10)

    def draw_grid(self, canvas):
        self.tile_rects = []
        page_size = self.rows * self.columns
        start = self.page_index * page_size
        page_items = self.visible_images[start : start + page_size]

        for local_index, (class_name, image_path) in enumerate(page_items):
            absolute_index = start + local_index
            row = local_index // self.columns
            column = local_index % self.columns

            x1 = column * self.tile_width
            y1 = self.header_height + row * self.tile_height
            x2 = x1 + self.tile_width
            y2 = y1 + self.tile_height
            self.tile_rects.append((x1, y1, x2, y2, absolute_index))

            selected = absolute_index == self.selected_index
            marked = self.relative_key(image_path) in self.marks
            border_color = (0, 185, 255) if selected else (190, 190, 190)
            fill_color = (245, 235, 160) if marked else (255, 255, 255)

            cv2.rectangle(canvas, (x1 + 4, y1 + 4), (x2 - 4, y2 - 4), fill_color, -1)
            cv2.rectangle(canvas, (x1 + 4, y1 + 4), (x2 - 4, y2 - 4), border_color, 3 if selected else 1)

            thumb = self.read_scaled_image(
                image_path,
                self.tile_width - 18,
                self.tile_height - self.label_height - 18,
            )
            thumb_height, thumb_width = thumb.shape[:2]
            image_x = x1 + (self.tile_width - thumb_width) // 2
            image_y = y1 + 10
            canvas[image_y : image_y + thumb_height, image_x : image_x + thumb_width] = thumb

            label = image_path.name
            if self.class_names[self.class_index] == "ALL":
                label = f"{class_name} / {label}"
            if marked:
                label = f"* {label}"

            self.put_text(
                canvas,
                self.trim_text(label, 24),
                x1 + 10,
                y2 - 12,
                scale=0.42,
                color=(25, 25, 25),
                thickness=1,
            )

    def draw_footer(self, canvas):
        width = canvas.shape[1]
        y1 = canvas.shape[0] - self.footer_height
        cv2.rectangle(canvas, (0, y1), (width, canvas.shape[0]), (35, 35, 35), -1)

        page_size = self.rows * self.columns
        total_pages = max(1, (len(self.visible_images) + page_size - 1) // page_size)
        start = self.page_index * page_size + 1 if self.visible_images else 0
        end = min((self.page_index + 1) * page_size, len(self.visible_images))
        selected = self.selected_index + 1 if self.visible_images else 0
        info = f"Page {self.page_index + 1}/{total_pages} | Images {start}-{end} | Selected {selected}/{len(self.visible_images)}"
        self.put_text(canvas, info, 12, y1 + 30, scale=0.58, color=(255, 255, 255), thickness=2)

    def read_scaled_image(self, image_path, max_width, max_height):
        image = cv2.imread(str(image_path))
        if image is None:
            return np.full((max_height, max_width, 3), 220, dtype=np.uint8)

        height, width = image.shape[:2]
        scale = min(max_width / width, max_height / height)
        new_width = max(1, int(width * scale))
        new_height = max(1, int(height * scale))
        return cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)

    def open_preview(self):
        if not self.visible_images:
            return

        class_name, image_path = self.visible_images[self.selected_index]
        image = cv2.imread(str(image_path))
        if image is None:
            return

        preview = self.fit_into_canvas(image, 1100, 720)
        marked = self.relative_key(image_path) in self.marks
        info = (
            f"{self.selected_index + 1}/{len(self.visible_images)} | "
            f"{class_name} | {image_path.name} | Marked: {'yes' if marked else 'no'}"
        )
        cv2.rectangle(preview, (0, 0), (preview.shape[1], 42), (20, 20, 20), -1)
        self.put_text(preview, info, 12, 28, scale=0.65, color=(255, 255, 255), thickness=2)
        cv2.imshow(self.preview_window_name, preview)

    @staticmethod
    def fit_into_canvas(image, max_width, max_height):
        height, width = image.shape[:2]
        scale = min(max_width / width, max_height / height, 1.0)
        new_width = max(1, int(width * scale))
        new_height = max(1, int(height * scale))
        resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
        canvas = np.full((max_height, max_width, 3), 30, dtype=np.uint8)
        x = (max_width - new_width) // 2
        y = (max_height - new_height) // 2
        canvas[y : y + new_height, x : x + new_width] = resized
        return canvas

    def on_mouse(self, event, x, y, _flags, _param):
        if event != cv2.EVENT_LBUTTONDOWN:
            return

        for x1, y1, x2, y2, absolute_index in self.tile_rects:
            if x1 <= x <= x2 and y1 <= y <= y2:
                self.selected_index = absolute_index
                self.open_preview()
                return

    def next_page(self):
        page_size = self.rows * self.columns
        total_pages = max(1, (len(self.visible_images) + page_size - 1) // page_size)
        if self.page_index >= total_pages - 1:
            return

        self.page_index += 1
        self.selected_index = min(self.page_index * page_size, max(0, len(self.visible_images) - 1))

    def previous_page(self):
        if self.page_index <= 0:
            return

        self.page_index -= 1
        self.selected_index = self.page_index * self.rows * self.columns

    def change_class(self, delta):
        self.class_index = (self.class_index + delta) % len(self.class_names)
        self.apply_filters(reset_sample=False)

    def select_class_by_number(self, index):
        if index >= len(self.class_names):
            return

        self.class_index = index
        self.apply_filters(reset_sample=False)

    def toggle_mark(self):
        if not self.visible_images:
            return

        _class_name, image_path = self.visible_images[self.selected_index]
        key = self.relative_key(image_path)
        if key in self.marks:
            self.marks.remove(key)
        else:
            self.marks.add(key)
        self.save_marks()

    def relative_key(self, image_path):
        return image_path.resolve().relative_to(self.dataset_path).as_posix()

    @staticmethod
    def put_text(canvas, text, x, y, scale, color, thickness):
        cv2.putText(
            canvas,
            text,
            (x, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            scale,
            color,
            thickness,
            cv2.LINE_AA,
        )

    @staticmethod
    def trim_text(text, max_chars):
        if len(text) <= max_chars:
            return text
        return text[: max_chars - 3] + "..."


def parse_args():
    parser = argparse.ArgumentParser(description="Browse ImageFolder-style datasets in an OpenCV thumbnail grid.")
    parser.add_argument(
        "dataset",
        nargs="?",
        help="Path to a dataset folder. The folder should contain one subfolder per class.",
    )
    parser.add_argument("--rows", type=int, default=None, help="Thumbnail grid rows.")
    parser.add_argument("--columns", type=int, default=None, help="Thumbnail grid columns.")
    parser.add_argument("--sample-size", type=int, default=None, help="Random sample size per class.")
    return parser.parse_args()


def main():
    args = parse_args()
    dataset = Path(args.dataset or dataset_folder)
    if not dataset.is_absolute():
        dataset = project_root / dataset

    viewer = DatasetViewer(
        dataset_path=dataset,
        rows=args.rows or grid_rows,
        columns=args.columns or grid_columns,
        sample_size=args.sample_size or random_sample_size,
    )
    viewer.run()


if __name__ == "__main__":
    main()

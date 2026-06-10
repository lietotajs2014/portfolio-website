import json
import re
import shutil
import tkinter as tk
import hashlib
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from PIL import Image, ImageOps, ImageTk


ROOT = Path(__file__).resolve().parent
UPLOAD_DIR = ROOT / "assets" / "uploads"
DATA_FILE = ROOT / "portfolio-data.js"
HERO_MARQUEE_FILE = ROOT / "assets" / "hero-marquee.jpg"

PROJECTS = [
    ("nature", "Daba"),
    ("art", "Māksla"),
    ("events", "Pasākumi"),
    ("portraits", "Portreti"),
    ("sports", "Sports"),
    ("street", "Street"),
    ("photoshop", "Photoshop"),
    ("gimnazijas-laiki", "Gimnazijas Laiki"),
    ("dzejas-krajums", "Dzejas krajums"),
    ("video-editing", "Video montēšana"),
]

SHOWCASE_WORKS = [
    ("layout", "gimnazijas-laiki", "Gimnazijas Laiki"),
    ("layout", "dzejas-krajums", "Dzejas krajums"),
    ("video", "video-editing", "12. klases Žetonfilma"),
    ("video", "video-editing", "Saulrieši"),
    ("video", "video-editing", "Lucid Dreaming"),
    ("video", "video-editing", "Castle Crashers theme"),
]

IMAGE_TYPES = (
    ("Images", "*.jpg *.jpeg *.png *.webp *.gif"),
    ("All files", "*.*"),
)

TARGET_TYPES = (
    ("Documents and videos", "*.pdf *.mp4 *.mov *.m4v *.webm"),
    ("All files", "*.*"),
)


def project_key(label):
    for key, project_label in PROJECTS:
        if project_label == label:
            return key
    return PROJECTS[0][0]


def project_label(key):
    for project_key_value, label in PROJECTS:
        if project_key_value == key:
            return label
    return key


def slugify(value):
    safe = re.sub(r"[^a-zA-Z0-9._-]+", "-", value.strip().lower())
    return safe.strip("-") or "image"


def unique_destination(source):
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    stem = slugify(source.stem)
    suffix = source.suffix.lower()
    candidate = UPLOAD_DIR / f"{stem}{suffix}"
    counter = 2

    while candidate.exists():
        candidate = UPLOAD_DIR / f"{stem}-{counter}{suffix}"
        counter += 1

    return candidate


def path_from_value(value):
    candidate = Path(value)
    if candidate.exists():
        return candidate

    root_candidate = ROOT / value
    if root_candidate.exists():
        return root_candidate

    return candidate


def is_inside_root(path):
    try:
        path.resolve().relative_to(ROOT.resolve())
        return True
    except ValueError:
        return False


def copy_asset_to_uploads(source):
    if is_inside_root(source):
        return source.resolve().relative_to(ROOT.resolve()).as_posix()

    destination = unique_destination(source)
    shutil.copy2(source, destination)
    return destination.relative_to(ROOT).as_posix()


def file_hash(path):
    digest = hashlib.sha256()
    with path.open("rb") as image_file:
        for chunk in iter(lambda: image_file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def find_duplicate_image(data, source_hash):
    for key, items in data.items():
        for index, item in enumerate(items):
            if not isinstance(item, dict):
                continue

            existing_src = item.get("src")
            if not existing_src:
                continue

            existing_path = ROOT / existing_src
            if existing_path.exists() and file_hash(existing_path) == source_hash:
                return key, index, item

    return None


def import_image_source(source, data):
    source_hash = file_hash(source)
    duplicate = find_duplicate_image(data, source_hash)
    if duplicate:
        _existing_key, _index, existing_item = duplicate
        existing_src = existing_item.get("src")
        if existing_src:
            return existing_src

    return copy_asset_to_uploads(source)


def showcase_work_by_label(label):
    for work in SHOWCASE_WORKS:
        if work[2] == label:
            return work
    return SHOWCASE_WORKS[0]


def load_data():
    if not DATA_FILE.exists():
        return {}

    content = DATA_FILE.read_text(encoding="utf-8")
    match = re.search(r"window\.PORTFOLIO_ITEMS\s*=\s*(.*?);?\s*$", content, re.S)
    if not match:
        return {}

    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError:
        messagebox.showwarning("Data error", "portfolio-data.js could not be read. A new data file will be written.")
        return {}


def cover_resize(image, size):
    target_width, target_height = size
    image_ratio = image.width / image.height
    target_ratio = target_width / target_height

    if image_ratio > target_ratio:
        new_height = target_height
        new_width = round(target_height * image_ratio)
    else:
        new_width = target_width
        new_height = round(target_width / image_ratio)

    image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    left = (new_width - target_width) // 2
    top = (new_height - target_height) // 2
    return image.crop((left, top, left + target_width, top + target_height))


def generate_hero_marquee(data):
    image_sources = []
    seen = set()

    for items in data.values():
        if not isinstance(items, list):
            continue

        for item in items:
            if not isinstance(item, dict):
                continue

            src = item.get("src")
            if src and src not in seen:
                seen.add(src)
                image_sources.append(ROOT / src)

    image_sources = [path for path in image_sources if path.exists()]
    if not image_sources:
        return

    rows = 6
    columns = 42
    tile_width = 260
    tile_height = 174
    gap = 10
    width = (columns * tile_width) + ((columns - 1) * gap)
    height = (rows * tile_height) + ((rows - 1) * gap)
    canvas = Image.new("RGB", (width, height), (61, 36, 16))
    tile_count = rows * columns

    for tile_index in range(tile_count):
        source = image_sources[tile_index % len(image_sources)]
        column = tile_index // rows
        row = tile_index % rows
        x = column * (tile_width + gap)
        y = row * (tile_height + gap)

        try:
            with Image.open(source) as image:
                image.draft("RGB", (tile_width * 2, tile_height * 2))
                image = ImageOps.exif_transpose(image).convert("RGB")
                tile = cover_resize(image, (tile_width, tile_height))
                canvas.paste(tile, (x, y))
        except Exception:
            continue

    HERO_MARQUEE_FILE.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(HERO_MARQUEE_FILE, "JPEG", quality=82, optimize=True, progressive=True)


def save_data(data):
    payload = json.dumps(data, indent=2, ensure_ascii=False)
    DATA_FILE.write_text(f"window.PORTFOLIO_ITEMS = {payload};\n", encoding="utf-8")
    generate_hero_marquee(data)


class PortfolioManager(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Portfolio Image Manager")
        self.geometry("1040x680")
        self.pending = {}
        self.thumbnail_cache = {}
        self.existing_load_after_id = None

        self.project_var = tk.StringVar(value=PROJECTS[0][1])
        self.caption_var = tk.StringVar()
        self.video_url_var = tk.StringVar()
        self.filter_var = tk.StringVar(value=PROJECTS[0][1])
        self.status_var = tk.StringVar()
        self.existing_project_var = tk.StringVar(value=PROJECTS[0][1])
        self.existing_caption_var = tk.StringVar()
        self.existing_link_var = tk.StringVar()
        self.showcase_work_var = tk.StringVar(value=SHOWCASE_WORKS[0][2])
        self.showcase_link_var = tk.StringVar()
        self.showcase_status_var = tk.StringVar()
        self.showcase_paths = []

        self.build_ui()
        self.protocol("WM_DELETE_WINDOW", self.close_app)
        self.after(100, self.refresh_existing_images)

    def build_ui(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        import_tab = ttk.Frame(notebook)
        showcase_tab = ttk.Frame(notebook)
        manage_tab = ttk.Frame(notebook)
        notebook.add(import_tab, text="Add images")
        notebook.add(showcase_tab, text="Video / maketēšana")
        notebook.add(manage_tab, text="Added images")

        toolbar = ttk.Frame(import_tab, padding=12)
        toolbar.pack(fill="x")

        ttk.Label(toolbar, text="Classification").grid(row=0, column=0, sticky="w")
        self.project_select = ttk.Combobox(
            toolbar,
            textvariable=self.project_var,
            values=[label for _, label in PROJECTS],
            state="readonly",
            width=28,
        )
        self.project_select.grid(row=1, column=0, sticky="ew", padx=(0, 12))

        ttk.Label(toolbar, text="Text under image").grid(row=0, column=1, sticky="w")
        self.caption_entry = ttk.Entry(toolbar, textvariable=self.caption_var)
        self.caption_entry.grid(row=1, column=1, sticky="ew", padx=(0, 12))

        ttk.Label(toolbar, text="Document/video link").grid(row=0, column=2, sticky="w")
        self.video_url_entry = ttk.Entry(toolbar, textvariable=self.video_url_var)
        self.video_url_entry.grid(row=1, column=2, sticky="ew", padx=(0, 12))

        ttk.Button(toolbar, text="Add images", command=self.add_images).grid(row=1, column=3, padx=(0, 8))
        ttk.Button(toolbar, text="Apply to selected", command=self.apply_to_selected).grid(row=1, column=4, padx=(0, 8))
        ttk.Button(toolbar, text="Remove selected", command=self.remove_selected).grid(row=1, column=5)

        toolbar.columnconfigure(1, weight=1)
        toolbar.columnconfigure(2, weight=1)

        columns = ("file", "project", "caption", "video_url")
        self.tree = ttk.Treeview(import_tab, columns=columns, show="headings", selectmode="extended")
        self.tree.heading("file", text="Image")
        self.tree.heading("project", text="Classification")
        self.tree.heading("caption", text="Text")
        self.tree.heading("video_url", text="Document/video link")
        self.tree.column("file", width=360)
        self.tree.column("project", width=180)
        self.tree.column("caption", width=250)
        self.tree.column("video_url", width=260)
        self.tree.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        footer = ttk.Frame(import_tab, padding=(12, 0, 12, 12))
        footer.pack(fill="x")
        ttk.Button(footer, text="Import to website", command=self.import_images).pack(side="right")
        ttk.Label(
            footer,
            text="Tip: select rows, change classification/text/link above, then click Apply to selected.",
        ).pack(side="left")

        manage_toolbar = ttk.Frame(manage_tab, padding=12)
        manage_toolbar.pack(fill="x")

        ttk.Label(manage_toolbar, text="Show category").grid(row=0, column=0, sticky="w")
        self.filter_select = ttk.Combobox(
            manage_toolbar,
            textvariable=self.filter_var,
            values=["All categories", *[label for _, label in PROJECTS]],
            state="readonly",
            width=28,
        )
        self.filter_select.grid(row=1, column=0, sticky="w", padx=(0, 12))
        self.filter_select.bind("<<ComboboxSelected>>", lambda _event: self.refresh_existing_images())

        ttk.Button(manage_toolbar, text="Refresh", command=self.refresh_existing_images).grid(row=1, column=1, padx=(0, 8))
        ttk.Button(manage_toolbar, text="Toggle highlight", command=self.toggle_highlight).grid(row=1, column=2, padx=(0, 8))
        ttk.Button(manage_toolbar, text="Remove from website", command=self.remove_existing_images).grid(row=1, column=3)

        ttk.Label(manage_toolbar, text="Edit category").grid(row=2, column=0, sticky="w", pady=(12, 0))
        self.existing_project_select = ttk.Combobox(
            manage_toolbar,
            textvariable=self.existing_project_var,
            values=[label for _, label in PROJECTS],
            state="readonly",
            width=28,
        )
        self.existing_project_select.grid(row=3, column=0, sticky="ew", padx=(0, 12))

        ttk.Label(manage_toolbar, text="Edit text").grid(row=2, column=1, sticky="w", pady=(12, 0))
        self.existing_caption_entry = ttk.Entry(manage_toolbar, textvariable=self.existing_caption_var)
        self.existing_caption_entry.grid(row=3, column=1, sticky="ew", padx=(0, 12))

        ttk.Label(manage_toolbar, text="Edit document/video link").grid(row=2, column=2, sticky="w", pady=(12, 0))
        self.existing_link_entry = ttk.Entry(manage_toolbar, textvariable=self.existing_link_var)
        self.existing_link_entry.grid(row=3, column=2, sticky="ew", padx=(0, 12))

        ttk.Button(manage_toolbar, text="Update selected", command=self.update_existing_images).grid(row=3, column=3)

        manage_toolbar.columnconfigure(1, weight=1)
        manage_toolbar.columnconfigure(2, weight=1)

        style = ttk.Style(self)
        style.configure("Existing.Treeview", rowheight=82)

        existing_columns = ("project", "caption", "highlighted", "video_url", "src")
        self.existing_tree = ttk.Treeview(
            manage_tab,
            columns=existing_columns,
            show="tree headings",
            selectmode="extended",
            style="Existing.Treeview",
        )
        self.existing_tree.heading("#0", text="Preview")
        self.existing_tree.heading("project", text="Category")
        self.existing_tree.heading("caption", text="Text")
        self.existing_tree.heading("highlighted", text="Highlighted")
        self.existing_tree.heading("video_url", text="Document/video link")
        self.existing_tree.heading("src", text="File")
        self.existing_tree.column("#0", width=96, stretch=False)
        self.existing_tree.column("project", width=160, stretch=False)
        self.existing_tree.column("caption", width=230)
        self.existing_tree.column("highlighted", width=110, stretch=False)
        self.existing_tree.column("video_url", width=220)
        self.existing_tree.column("src", width=260)
        self.existing_tree.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self.existing_tree.bind("<<TreeviewSelect>>", self.load_existing_edit_fields)

        manage_footer = ttk.Frame(manage_tab, padding=(12, 0, 12, 12))
        manage_footer.pack(fill="x")
        ttk.Label(
            manage_footer,
            text="Highlight makes the selected image larger. Document/video links open when that work is clicked.",
        ).pack(side="left")
        ttk.Label(manage_footer, textvariable=self.status_var).pack(side="right")
        self.build_showcase_tab(showcase_tab)

    def build_showcase_tab(self, parent):
        toolbar = ttk.Frame(parent, padding=12)
        toolbar.pack(fill="x")

        ttk.Label(toolbar, text="Work").grid(row=0, column=0, sticky="w")
        self.showcase_work_select = ttk.Combobox(
            toolbar,
            textvariable=self.showcase_work_var,
            values=[label for _kind, _key, label in SHOWCASE_WORKS],
            state="readonly",
            width=34,
        )
        self.showcase_work_select.grid(row=1, column=0, sticky="ew", padx=(0, 12))
        self.showcase_work_select.bind("<<ComboboxSelected>>", lambda _event: self.load_showcase_work())

        ttk.Label(toolbar, text="Document/video link or file").grid(row=0, column=1, sticky="w")
        self.showcase_link_entry = ttk.Entry(toolbar, textvariable=self.showcase_link_var)
        self.showcase_link_entry.grid(row=1, column=1, sticky="ew", padx=(0, 8))

        ttk.Button(toolbar, text="Choose file", command=self.choose_showcase_target).grid(row=1, column=2, padx=(0, 8))
        ttk.Button(toolbar, text="Choose 3-5 images", command=self.choose_showcase_images).grid(row=1, column=3, padx=(0, 8))
        ttk.Button(toolbar, text="Save work", command=self.save_showcase_work).grid(row=1, column=4)

        toolbar.columnconfigure(1, weight=1)

        help_text = (
            "Use this for Maketēšana and Video montēšana buttons. "
            "A local PDF/video file will be copied to assets/uploads; a pasted URL will be used as-is."
        )
        ttk.Label(parent, text=help_text, padding=(12, 0, 12, 8)).pack(fill="x")

        columns = ("file",)
        self.showcase_tree = ttk.Treeview(parent, columns=columns, show="headings", selectmode="extended")
        self.showcase_tree.heading("file", text="Slideshow image")
        self.showcase_tree.column("file", width=880)
        self.showcase_tree.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        footer = ttk.Frame(parent, padding=(12, 0, 12, 12))
        footer.pack(fill="x")
        ttk.Button(footer, text="Remove selected image", command=self.remove_showcase_selected).pack(side="left")
        ttk.Button(footer, text="Clear images", command=self.clear_showcase_images).pack(side="left", padx=(8, 0))
        ttk.Label(footer, textvariable=self.showcase_status_var).pack(side="right")

        self.load_showcase_work()

    def selected_showcase_work(self):
        return showcase_work_by_label(self.showcase_work_var.get())

    def current_showcase_items(self, data, kind, key, title):
        items = data.get(key, [])
        if kind == "video":
            return [
                item for item in items
                if isinstance(item, dict) and item.get("caption") == title
            ]

        showcase_items = [
            item for item in items
            if isinstance(item, dict) and item.get("showcase")
        ]
        if showcase_items:
            return showcase_items

        return [
            item for item in items
            if isinstance(item, dict) and item.get("featured")
        ]

    def load_showcase_work(self):
        if not hasattr(self, "showcase_tree"):
            return

        kind, key, title = self.selected_showcase_work()
        data = load_data()
        items = self.current_showcase_items(data, kind, key, title)
        link = next((item.get("videoUrl", "") for item in items if item.get("videoUrl")), "")

        self.showcase_link_var.set(link)
        self.showcase_paths = [
            ROOT / item.get("src", "")
            for item in items
            if item.get("src")
        ][:5]
        self.refresh_showcase_images()

    def refresh_showcase_images(self):
        rows = self.showcase_tree.get_children()
        if rows:
            self.showcase_tree.delete(*rows)

        for path in self.showcase_paths:
            self.showcase_tree.insert("", "end", values=(str(path),))

        count = len(self.showcase_paths)
        self.showcase_status_var.set(f"{count} selected image(s); choose 3-5 before saving.")

    def choose_showcase_target(self):
        path = filedialog.askopenfilename(title="Select document or video", filetypes=TARGET_TYPES)
        if path:
            self.showcase_link_var.set(path)

    def choose_showcase_images(self):
        paths = filedialog.askopenfilenames(title="Select 3-5 slideshow images", filetypes=IMAGE_TYPES)
        if not paths:
            return

        if len(paths) < 3 or len(paths) > 5:
            messagebox.showwarning("Image count", "Choose 3 to 5 images for this slideshow.")
            return

        self.showcase_paths = [Path(path) for path in paths]
        self.refresh_showcase_images()

    def remove_showcase_selected(self):
        selected = set(self.showcase_tree.selection())
        if not selected:
            messagebox.showinfo("No selection", "Select one or more slideshow images first.")
            return

        remaining = []
        for item_id in self.showcase_tree.get_children():
            values = self.showcase_tree.item(item_id, "values")
            if item_id not in selected and values:
                remaining.append(Path(values[0]))

        self.showcase_paths = remaining
        self.refresh_showcase_images()

    def clear_showcase_images(self):
        self.showcase_paths = []
        self.refresh_showcase_images()

    def resolved_showcase_link(self):
        value = self.showcase_link_var.get().strip()
        if not value:
            return ""

        target_path = path_from_value(value)
        if target_path.exists() and target_path.is_file():
            return copy_asset_to_uploads(target_path)

        return value

    def save_showcase_work(self):
        kind, key, title = self.selected_showcase_work()
        link = self.resolved_showcase_link()

        if not link:
            messagebox.showwarning("Missing link", "Add a document/video link or choose a document/video file.")
            return

        if len(self.showcase_paths) < 3 or len(self.showcase_paths) > 5:
            messagebox.showwarning("Image count", "Choose 3 to 5 slideshow images before saving.")
            return

        data = load_data()
        new_items = []

        for path in self.showcase_paths:
            source = path_from_value(str(path))
            if not source.exists() or not source.is_file():
                messagebox.showwarning("Missing image", f"Image not found:\n{path}")
                return

            new_items.append({
                "src": import_image_source(source, data),
                "caption": title,
                "featured": True,
                "showcase": True,
                "videoUrl": link,
            })

        if kind == "video":
            existing_items = [
                item for item in data.get(key, [])
                if not (
                    isinstance(item, dict)
                    and item.get("caption") == title
                )
            ]
        else:
            existing_items = [
                item for item in data.get(key, [])
                if not (isinstance(item, dict) and item.get("showcase"))
            ]

        data[key] = existing_items + new_items
        save_data(data)
        self.showcase_link_var.set(link)
        self.showcase_paths = [ROOT / item["src"] for item in new_items]
        self.refresh_showcase_images()
        self.refresh_existing_images()
        messagebox.showinfo("Saved", f"Saved {title} with {len(new_items)} slideshow image(s).")

    def add_images(self):
        paths = filedialog.askopenfilenames(title="Select images", filetypes=IMAGE_TYPES)
        if not paths:
            return

        label = self.project_var.get()
        caption = self.caption_var.get().strip()
        video_url = self.video_url_var.get().strip()

        for path in paths:
            item_id = self.tree.insert("", "end", values=(path, label, caption, video_url))
            self.pending[item_id] = {
                "path": Path(path),
                "project": project_key(label),
                "caption": caption,
                "video_url": video_url,
            }

    def apply_to_selected(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("No selection", "Select one or more rows first.")
            return

        label = self.project_var.get()
        key = project_key(label)
        caption = self.caption_var.get().strip()
        video_url = self.video_url_var.get().strip()

        for item_id in selection:
            values = list(self.tree.item(item_id, "values"))
            values[1] = label
            values[2] = caption
            values[3] = video_url
            self.tree.item(item_id, values=values)
            self.pending[item_id]["project"] = key
            self.pending[item_id]["caption"] = caption
            self.pending[item_id]["video_url"] = video_url

    def remove_selected(self):
        for item_id in self.tree.selection():
            self.pending.pop(item_id, None)
            self.tree.delete(item_id)

    def import_images(self):
        if not self.pending:
            messagebox.showinfo("Nothing to import", "Add images first.")
            return

        data = load_data()
        imported_count = 0
        replaced_count = 0

        for item in self.pending.values():
            source = item["path"]
            if not source.exists():
                continue

            source_hash = file_hash(source)
            duplicate = find_duplicate_image(data, source_hash)
            key = item["project"]

            if duplicate:
                existing_key, index, existing_item = duplicate
                existing_src = existing_item.get("src", "")
                existing_path = ROOT / existing_src

                if existing_path.exists() and source.resolve() != existing_path.resolve():
                    shutil.copy2(source, existing_path)

                replacement = {
                    "src": existing_src,
                    "caption": item["caption"],
                    "featured": bool(existing_item.get("featured")) or key == "video-editing",
                }
                if item.get("video_url"):
                    replacement["videoUrl"] = item["video_url"]
                elif existing_item.get("videoUrl"):
                    replacement["videoUrl"] = existing_item["videoUrl"]

                if existing_key == key:
                    data[existing_key][index] = replacement
                else:
                    data[existing_key].pop(index)
                    data.setdefault(key, []).append(replacement)

                replaced_count += 1
            else:
                destination = unique_destination(source)
                shutil.copy2(source, destination)

                relative_path = destination.relative_to(ROOT).as_posix()
                new_item = {
                    "src": relative_path,
                    "caption": item["caption"],
                    "featured": key == "video-editing",
                }
                if item.get("video_url"):
                    new_item["videoUrl"] = item["video_url"]
                data.setdefault(key, []).append(new_item)
                imported_count += 1

        save_data(data)
        self.pending.clear()
        for item_id in self.tree.get_children():
            self.tree.delete(item_id)
        self.refresh_existing_images()

        messagebox.showinfo(
            "Imported",
            f"Imported {imported_count} image(s).\nReplaced {replaced_count} duplicate image(s).",
        )

    def get_thumbnail(self, relative_src):
        if not relative_src:
            return None

        image_path = ROOT / relative_src
        if not image_path.exists():
            return None

        cache_key = (relative_src, image_path.stat().st_mtime_ns)
        if cache_key in self.thumbnail_cache:
            return self.thumbnail_cache[cache_key]

        try:
            with Image.open(image_path) as image:
                image.draft("RGB", (144, 144))
                image = ImageOps.exif_transpose(image)
                image.thumbnail((72, 72))
                canvas = Image.new("RGBA", (72, 72), (234, 209, 178, 255))
                x = (72 - image.width) // 2
                y = (72 - image.height) // 2
                canvas.paste(image.convert("RGBA"), (x, y))
                thumbnail = ImageTk.PhotoImage(canvas)
        except Exception:
            return None

        self.thumbnail_cache[cache_key] = thumbnail
        return thumbnail

    def selected_filter_key(self):
        label = self.filter_var.get()
        if label == "All categories":
            return None
        return project_key(label)

    def refresh_existing_images(self):
        if not hasattr(self, "existing_tree"):
            return

        if self.existing_load_after_id:
            self.after_cancel(self.existing_load_after_id)
            self.existing_load_after_id = None

        existing_rows = self.existing_tree.get_children()
        if existing_rows:
            self.existing_tree.delete(*existing_rows)

        data = load_data()
        filter_key = self.selected_filter_key()
        rows_to_load = []

        for key, label in PROJECTS:
            if filter_key and key != filter_key:
                continue

            for index, item in enumerate(data.get(key, [])):
                if not isinstance(item, dict):
                    continue
                rows_to_load.append((key, label, index, item))

        self.status_var.set(f"Loading {len(rows_to_load)} image(s)...")
        self.load_existing_image_batch(rows_to_load, 0)

    def load_existing_image_batch(self, rows, start):
        batch_size = 10
        end = min(start + batch_size, len(rows))

        for key, label, index, item in rows[start:end]:
            src = item.get("src", "")
            caption = item.get("caption", "")
            highlighted = "Yes" if item.get("featured") else "No"
            video_url = item.get("videoUrl", "")
            image = self.get_thumbnail(src)
            self.existing_tree.insert(
                "",
                "end",
                iid=f"{key}:{index}",
                image=image,
                values=(label, caption, highlighted, video_url, src),
            )

        if end < len(rows):
            self.status_var.set(f"Loaded {end} of {len(rows)} image(s)...")
            self.existing_load_after_id = self.after(
                20,
                lambda: self.load_existing_image_batch(rows, end),
            )
        else:
            self.existing_load_after_id = None
            self.status_var.set(f"Showing {len(rows)} image(s)")

    def selected_existing_items(self):
        selected = []
        for item_id in self.existing_tree.selection():
            try:
                key, index_text = item_id.rsplit(":", 1)
                selected.append((key, int(index_text)))
            except ValueError:
                continue
        return selected

    def load_existing_edit_fields(self, _event=None):
        selected = self.selected_existing_items()
        if not selected:
            return

        key, index = selected[0]
        data = load_data()
        items = data.get(key, [])
        if not (0 <= index < len(items)) or not isinstance(items[index], dict):
            return

        item = items[index]
        self.existing_project_var.set(project_label(key))
        self.existing_caption_var.set(item.get("caption", ""))
        self.existing_link_var.set(item.get("videoUrl", ""))

    def update_existing_images(self):
        selected = self.selected_existing_items()
        if not selected:
            messagebox.showinfo("No selection", "Select one or more added images first.")
            return

        new_key = project_key(self.existing_project_var.get())
        caption = self.existing_caption_var.get().strip()
        link = self.existing_link_var.get().strip()
        data = load_data()
        updated_count = 0

        for key, index in sorted(selected, key=lambda value: (value[0], value[1]), reverse=True):
            items = data.get(key, [])
            if not (0 <= index < len(items)) or not isinstance(items[index], dict):
                continue

            item = items[index]
            item["caption"] = caption
            if link:
                item["videoUrl"] = link
            else:
                item.pop("videoUrl", None)

            if key == new_key:
                items[index] = item
            else:
                items.pop(index)
                data.setdefault(new_key, []).append(item)

            updated_count += 1

        save_data(data)
        self.refresh_existing_images()
        messagebox.showinfo("Updated", f"Updated {updated_count} image(s).")

    def remove_existing_images(self):
        selected = self.selected_existing_items()
        if not selected:
            messagebox.showinfo("No selection", "Select one or more added images first.")
            return

        if not messagebox.askyesno("Remove images", "Remove selected image(s) from the website data?"):
            return

        data = load_data()
        for key, index in sorted(selected, key=lambda value: (value[0], value[1]), reverse=True):
            items = data.get(key, [])
            if 0 <= index < len(items):
                items.pop(index)

        save_data(data)
        self.refresh_existing_images()

    def toggle_highlight(self):
        selected = self.selected_existing_items()
        if not selected:
            messagebox.showinfo("No selection", "Select one or more added images first.")
            return

        data = load_data()
        for key, index in selected:
            items = data.get(key, [])
            if 0 <= index < len(items) and isinstance(items[index], dict):
                items[index]["featured"] = not bool(items[index].get("featured"))

        save_data(data)
        self.refresh_existing_images()

    def close_app(self):
        if self.existing_load_after_id:
            self.after_cancel(self.existing_load_after_id)
            self.existing_load_after_id = None
        self.destroy()


if __name__ == "__main__":
    PortfolioManager().mainloop()

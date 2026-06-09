import json
import re
import shutil
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk


ROOT = Path(__file__).resolve().parent
UPLOAD_DIR = ROOT / "assets" / "uploads"
DATA_FILE = ROOT / "portfolio-data.js"

PROJECTS = [
    ("sports", "Sports"),
    ("events", "Events"),
    ("street", "Street"),
    ("art", "Art"),
    ("photo-manipulation", "Photo Manipulation"),
    ("poster-concepts", "Poster Concepts"),
    ("retouching", "Retouching"),
    ("gimnazijas-laiki", "Gimnazijas Laiki"),
    ("dzejas-krajums", "Dzejas krajums"),
]

IMAGE_TYPES = (
    ("Images", "*.jpg *.jpeg *.png *.webp *.gif"),
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


def save_data(data):
    payload = json.dumps(data, indent=2, ensure_ascii=False)
    DATA_FILE.write_text(f"window.PORTFOLIO_ITEMS = {payload};\n", encoding="utf-8")


class PortfolioManager(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Portfolio Image Manager")
        self.geometry("920x560")
        self.pending = {}

        self.project_var = tk.StringVar(value=PROJECTS[0][1])
        self.caption_var = tk.StringVar()

        self.build_ui()

    def build_ui(self):
        toolbar = ttk.Frame(self, padding=12)
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

        ttk.Button(toolbar, text="Add images", command=self.add_images).grid(row=1, column=2, padx=(0, 8))
        ttk.Button(toolbar, text="Apply to selected", command=self.apply_to_selected).grid(row=1, column=3, padx=(0, 8))
        ttk.Button(toolbar, text="Remove selected", command=self.remove_selected).grid(row=1, column=4)

        toolbar.columnconfigure(1, weight=1)

        columns = ("file", "project", "caption")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", selectmode="extended")
        self.tree.heading("file", text="Image")
        self.tree.heading("project", text="Classification")
        self.tree.heading("caption", text="Text")
        self.tree.column("file", width=360)
        self.tree.column("project", width=180)
        self.tree.column("caption", width=330)
        self.tree.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        footer = ttk.Frame(self, padding=(12, 0, 12, 12))
        footer.pack(fill="x")
        ttk.Button(footer, text="Import to website", command=self.import_images).pack(side="right")
        ttk.Label(
            footer,
            text="Tip: select rows, change classification/text above, then click Apply to selected.",
        ).pack(side="left")

    def add_images(self):
        paths = filedialog.askopenfilenames(title="Select images", filetypes=IMAGE_TYPES)
        if not paths:
            return

        label = self.project_var.get()
        caption = self.caption_var.get().strip()

        for path in paths:
            item_id = self.tree.insert("", "end", values=(path, label, caption))
            self.pending[item_id] = {
                "path": Path(path),
                "project": project_key(label),
                "caption": caption,
            }

    def apply_to_selected(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("No selection", "Select one or more rows first.")
            return

        label = self.project_var.get()
        key = project_key(label)
        caption = self.caption_var.get().strip()

        for item_id in selection:
            values = list(self.tree.item(item_id, "values"))
            values[1] = label
            values[2] = caption
            self.tree.item(item_id, values=values)
            self.pending[item_id]["project"] = key
            self.pending[item_id]["caption"] = caption

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

        for item in self.pending.values():
            source = item["path"]
            if not source.exists():
                continue

            destination = unique_destination(source)
            shutil.copy2(source, destination)

            relative_path = destination.relative_to(ROOT).as_posix()
            key = item["project"]
            data.setdefault(key, []).append({
                "src": relative_path,
                "caption": item["caption"],
            })
            imported_count += 1

        save_data(data)
        self.pending.clear()
        for item_id in self.tree.get_children():
            self.tree.delete(item_id)

        messagebox.showinfo(
            "Imported",
            f"Imported {imported_count} image(s).\nCommit and push the changed files to update the live site.",
        )


if __name__ == "__main__":
    PortfolioManager().mainloop()

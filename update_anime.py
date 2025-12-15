import tkinter as tk
from tkinter import ttk, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
import json
import os
import shutil

# --- CONFIGURATION ---
DATA_FILE = 'data/anime.json'
IMAGE_DIR = 'images'

# Ensure directories exist
os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
os.makedirs(IMAGE_DIR, exist_ok=True)

class AnimeUpdaterApp(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()

        self.title("Anime Manager (No Pillow)")
        self.geometry("400x550")
        self.resizable(False, False)

        # Variable to store the source path of the dropped image
        self.current_image_path = None

        self.create_widgets()

    def create_widgets(self):
        # --- TITLE ---
        lbl_title = tk.Label(self, text="Add New Entry", font=("Arial", 14, "bold"))
        lbl_title.pack(pady=10)

        # --- FORM CONTAINER ---
        form_frame = tk.Frame(self, padx=20)
        form_frame.pack(fill="x")

        # 1. Title Input
        tk.Label(form_frame, text="Title:", anchor="w").pack(fill="x")
        self.entry_title = tk.Entry(form_frame)
        self.entry_title.pack(fill="x", pady=(0, 10))

        # 2. Type Dropdown
        tk.Label(form_frame, text="Type:", anchor="w").pack(fill="x")
        self.combo_type = ttk.Combobox(form_frame, values=["Anime", "Manga"], state="readonly")
        self.combo_type.current(0)
        self.combo_type.pack(fill="x", pady=(0, 10))

        # 3. Rating Slider
        tk.Label(form_frame, text="Rating (1-5):", anchor="w").pack(fill="x")
        self.scale_rating = tk.Scale(form_frame, from_=1, to=5, orient="horizontal")
        self.scale_rating.set(5)
        self.scale_rating.pack(fill="x", pady=(0, 10))

        # 4. Description Input
        tk.Label(form_frame, text="Description:", anchor="w").pack(fill="x")
        self.text_desc = tk.Text(form_frame, height=4, font=("Arial", 10))
        self.text_desc.pack(fill="x", pady=(0, 10))

        # --- DRAG AND DROP ZONE ---
        tk.Label(self, text="Cover Image:", font=("Arial", 10, "bold")).pack(pady=(10, 5))
        
        self.drop_frame = tk.LabelFrame(self, width=200, height=80, bg="#eeeeee")
        self.drop_frame.pack(pady=5, padx=20, fill="x")
        self.drop_frame.pack_propagate(False)

        # Label inside drop zone
        self.lbl_drop_text = tk.Label(self.drop_frame, text="Drag & Drop Image Here", bg="#eeeeee", fg="#555")
        self.lbl_drop_text.place(relx=0.5, rely=0.5, anchor="center")

        # Enable Drag and Drop
        self.drop_frame.drop_target_register(DND_FILES)
        self.drop_frame.dnd_bind('<<Drop>>', self.drop_image)

        # --- SAVE BUTTON ---
        btn_save = tk.Button(self, text="SAVE ENTRY", bg="#f2c94c", fg="black", font=("Arial", 10, "bold"), command=self.save_entry)
        btn_save.pack(pady=20, fill="x", padx=40)

    def drop_image(self, event):
        # Get file path (tkinterdnd2 can sometimes wrap paths in {})
        file_path = event.data
        if file_path.startswith('{') and file_path.endswith('}'):
            file_path = file_path[1:-1]
        
        # Check extension
        if not file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.gif')):
            messagebox.showerror("Error", "Please drop a valid image file.")
            return

        self.current_image_path = file_path
        
        # Update text to show filename
        filename = os.path.basename(file_path)
        self.lbl_drop_text.config(text=f"Selected: {filename}", fg="green")

    def load_json(self):
        if not os.path.exists(DATA_FILE):
            return []
        try:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []

    def save_entry(self):
        # 1. Get Values
        title = self.entry_title.get().strip()
        anime_type = self.combo_type.get()
        rating = self.scale_rating.get()
        desc = self.text_desc.get("1.0", tk.END).strip()

        # 2. Validation
        if not title:
            messagebox.showwarning("Missing Data", "Please enter a Title.")
            return
        if not self.current_image_path:
            messagebox.showwarning("Missing Image", "Please drag and drop an image cover.")
            return

        # 3. Handle Image File
        try:
            filename = os.path.basename(self.current_image_path)
            destination = os.path.join(IMAGE_DIR, filename)
            
            # Copy file
            shutil.copy(self.current_image_path, destination)
            json_url = f"images/{filename}"
            
        except Exception as e:
            messagebox.showerror("File Error", f"Could not copy image: {e}")
            return

        # 4. Update JSON
        new_entry = {
            "title": title,
            "type": anime_type,
            "rating": rating,
            "cover_url": json_url,
            "description": desc
        }

        data = self.load_json()
        data.append(new_entry)

        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)

        # 5. Success & Reset
        messagebox.showinfo("Success", f"Added '{title}'!")
        self.reset_form()

    def reset_form(self):
        self.entry_title.delete(0, tk.END)
        self.text_desc.delete("1.0", tk.END)
        self.current_image_path = None
        self.lbl_drop_text.config(text="Drag & Drop Image Here", fg="#555")
        self.scale_rating.set(5)

if __name__ == "__main__":
    app = AnimeUpdaterApp()
    app.mainloop()
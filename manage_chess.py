import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD  # Import Drag-and-Drop
import json
import os
import shutil
from datetime import datetime

# --- CONFIGURATION ---
DB_FILE = "data/chess.json"
IMAGE_DIR = "images"

# Ensure directories exist
os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
os.makedirs(IMAGE_DIR, exist_ok=True)

class ChessBlogManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Chess Blog Manager")
        self.root.geometry("600x650")
        self.selected_image_path = None
        
        # Style configuration
        style = ttk.Style()
        style.theme_use('clam') 
        self.root.configure(bg="#f0f0f0")

        # --- Header ---
        header_frame = tk.Frame(root, bg="#34495e", height=60)
        header_frame.pack(fill="x")
        tk.Label(header_frame, text="♟️ New Chess Post", 
                 bg="#34495e", fg="white", font=("Helvetica", 16, "bold")).pack(pady=15)

        # --- Content Area ---
        content_frame = tk.Frame(root, bg="#f0f0f0", padx=20, pady=10)
        content_frame.pack(fill="both", expand=True)

        # 1. Image Drop Zone (Top Priority)
        self.drop_frame = tk.Frame(content_frame, bg="#dddddd", bd=2, relief="groove")
        self.drop_frame.pack(fill="x", pady=(0, 15))
        
        self.drop_label = tk.Label(
            self.drop_frame, 
            text="📂 DRAG IMAGE HERE\n(or click to browse)", 
            bg="#dddddd", fg="#555555",
            font=("Helvetica", 10, "bold"),
            height=4
        )
        self.drop_label.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Register Drop functionality
        self.drop_label.drop_target_register(DND_FILES)
        self.drop_label.dnd_bind('<<Drop>>', self.handle_drop)
        self.drop_label.bind("<Button-1>", self.browse_file) # Click fallback

        # 2. Title Input
        tk.Label(content_frame, text="Post Title:", bg="#f0f0f0", font=("Arial", 10, "bold")).pack(anchor="w")
        self.title_entry = ttk.Entry(content_frame, font=("Arial", 11))
        self.title_entry.pack(fill="x", pady=(5, 15))

        # 3. Content Input
        tk.Label(content_frame, text="Thoughts / Analysis:", bg="#f0f0f0", font=("Arial", 10, "bold")).pack(anchor="w")
        self.content_text = tk.Text(content_frame, height=10, font=("Arial", 11), borderwidth=1, relief="solid")
        self.content_text.pack(fill="both", expand=True, pady=(5, 15))

        # --- Action Buttons ---
        btn_frame = tk.Frame(root, bg="#f0f0f0", pady=10)
        btn_frame.pack(fill="x")

        tk.Button(btn_frame, text="Clear", command=self.clear_form, 
                  bg="#e74c3c", fg="white", font=("Arial", 10)).pack(side="left", padx=20)
        
        self.save_btn = tk.Button(btn_frame, text="💾 Save Post", command=self.save_post, 
                  bg="#2ecc71", fg="white", font=("Arial", 10, "bold"), padx=20, pady=5)
        self.save_btn.pack(side="right", padx=20)

    def handle_drop(self, event):
        """Handles the file drop event correctly handling spaces."""
        files = self.root.tk.splitlist(event.data)
        if files:
            self.load_image(files[0])

    def browse_file(self, event=None):
        filename = filedialog.askopenfilename(
            filetypes=[("Images", "*.jpg *.jpeg *.png *.webp")]
        )
        if filename:
            self.load_image(filename)

    def load_image(self, path):
        """Validates and stages the image."""
        if os.path.exists(path):
            self.selected_image_path = path
            filename = os.path.basename(path)
            
            # Visual Feedback
            self.drop_label.config(text=f"✅ SELECTED:\n{filename}", bg="#d4edda", fg="#155724")
            self.drop_frame.config(bg="#c3e6cb")
        else:
            messagebox.showerror("Error", f"Could not find file: {path}")

    def save_post(self):
        title = self.title_entry.get().strip()
        content = self.content_text.get("1.0", tk.END).strip()

        if not title or not content:
            messagebox.showwarning("Missing Info", "Please enter both a Title and Content.")
            return

        # Handle Image Copying
        saved_image_url = ""
        if self.selected_image_path:
            try:
                ext = os.path.splitext(self.selected_image_path)[1]
                safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-')).strip()
                new_filename = f"chess-{safe_title.replace(' ', '-').lower()}{ext}"
                dest_path = os.path.join(IMAGE_DIR, new_filename)
                
                shutil.copy(self.selected_image_path, dest_path)
                saved_image_url = f"images/{new_filename}"
            except Exception as e:
                messagebox.showerror("Image Error", f"Failed to process image: {e}")
                return

        # Load Data
        if os.path.exists(DB_FILE):
            try:
                with open(DB_FILE, 'r') as f:
                    data = json.load(f)
            except: data = []
        else: data = []

        # Create Entry
        new_post = {
            "id": len(data) + 1,
            "title": title,
            "date": datetime.now().strftime("%B %d, %Y"),
            "content": content,
            "image_url": saved_image_url
        }

        data.insert(0, new_post)

        try:
            with open(DB_FILE, 'w') as f:
                json.dump(data, f, indent=4)
            messagebox.showinfo("Success", "Chess post published successfully!")
            self.clear_form()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {e}")

    def clear_form(self):
        self.title_entry.delete(0, tk.END)
        self.content_text.delete("1.0", tk.END)
        self.selected_image_path = None
        
        # Reset Visuals
        self.drop_label.config(text="📂 DRAG IMAGE HERE\n(or click to browse)", bg="#dddddd", fg="#555555")
        self.drop_frame.config(bg="#dddddd")

if __name__ == "__main__":
    # Remember: We use TkinterDnD.Tk() instead of tk.Tk()
    root = TkinterDnD.Tk()
    app = ChessBlogManager(root)
    root.mainloop()
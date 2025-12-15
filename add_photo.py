import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
import os
import shutil
import json
from datetime import datetime

# --- CONFIGURATION ---
IMAGE_DIR = "images"
DB_FILE = "data/photography.json"

# Ensure directories exist
os.makedirs(IMAGE_DIR, exist_ok=True)
os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)

class PortfolioUploader:
    def __init__(self, master):
        self.master = master
        master.title("Portfolio Manager")
        master.geometry("600x450")
        
        # Apply a simple theme
        style = ttk.Style()
        style.theme_use('clam') # 'clam', 'alt', 'default', 'classic'

        # Variables
        self.source_path = None
        self.title_var = tk.StringVar()
        self.location_var = tk.StringVar()
        self.desc_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Waiting for image...")

        # --- MAIN LAYOUT (Grid) ---
        
        # 1. Drop Zone (Top Section)
        self.drop_frame = tk.Frame(master, bg="#dddddd", bd=2, relief="groove")
        self.drop_frame.pack(fill="x", padx=20, pady=20)
        
        self.drop_label = tk.Label(
            self.drop_frame, 
            text="📂 DRAG IMAGE HERE\n(or click to browse)", 
            bg="#dddddd", fg="#555555",
            font=("Helvetica", 12, "bold"),
            height=6
        )
        self.drop_label.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Register Drop functionality
        self.drop_label.drop_target_register(DND_FILES)
        self.drop_label.dnd_bind('<<Drop>>', self.handle_drop)
        self.drop_label.bind("<Button-1>", self.browse_file) # Click fallback

        # 2. Form Section (Middle Section)
        form_frame = ttk.Frame(master, padding="20 10 20 10")
        form_frame.pack(fill="both", expand=True)

        # Title
        ttk.Label(form_frame, text="Title:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", pady=5)
        ttk.Entry(form_frame, textvariable=self.title_var, width=50).grid(row=0, column=1, sticky="ew", pady=5)

        # Location
        ttk.Label(form_frame, text="Location:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky="w", pady=5)
        ttk.Entry(form_frame, textvariable=self.location_var, width=50).grid(row=1, column=1, sticky="ew", pady=5)

        # Description
        ttk.Label(form_frame, text="Description:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky="w", pady=5)
        ttk.Entry(form_frame, textvariable=self.desc_var, width=50).grid(row=2, column=1, sticky="ew", pady=5)

        form_frame.columnconfigure(1, weight=1) # Make input boxes expand

        # 3. Action Buttons (Bottom Section)
        btn_frame = ttk.Frame(master, padding="20 0 20 20")
        btn_frame.pack(fill="x")
        
        # Status Label
        self.status_lbl = tk.Label(btn_frame, textvariable=self.status_var, fg="gray", font=("Arial", 9))
        self.status_lbl.pack(side="left")

        # Save Button
        self.save_btn = tk.Button(
            btn_frame, 
            text="🚀 PROCESS & SAVE", 
            command=self.process_entry,
            bg="#2ecc71", fg="white", 
            font=("Arial", 10, "bold"),
            state="disabled", # Disabled until image is dropped
            padx=20, pady=5
        )
        self.save_btn.pack(side="right")

    def handle_drop(self, event):
        # --- CRITICAL FIX: Parse the file list correctly ---
        # event.data returns a string that might look like:
        # "{/home/user/file with spaces.jpg} /home/user/normal.jpg"
        # tk.splitlist handles the curly braces parsing automatically.
        files = self.master.tk.splitlist(event.data)
        
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
            self.source_path = path
            filename = os.path.basename(path)
            
            # Update GUI to show success
            self.drop_label.config(text=f"✅ READY TO UPLOAD:\n{filename}", bg="#d4edda", fg="#155724")
            self.drop_frame.config(bg="#c3e6cb") # Greenish border
            self.status_var.set(f"Selected: {filename}")
            self.status_lbl.config(fg="green")
            
            # Enable the save button
            self.save_btn.config(state="normal", bg="#28a745")
            
            # Auto-fill title if empty
            if not self.title_var.get():
                self.title_var.set(os.path.splitext(filename)[0].replace("-", " ").replace("_", " ").title())
        else:
            messagebox.showerror("Error", f"Could not find file: {path}")

    def process_entry(self):
        if not self.source_path:
            return

        title = self.title_var.get().strip()
        location = self.location_var.get().strip()
        desc = self.desc_var.get().strip()

        if not title:
            messagebox.showwarning("Missing Info", "Please enter a Title.")
            return

        try:
            # 1. Prepare Filename
            original_filename = os.path.basename(self.source_path)
            ext = os.path.splitext(original_filename)[1].lower()
            
            # Create a safe filename based on the Title (SEO friendly)
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-')).strip()
            safe_filename = safe_title.replace(" ", "-").lower() + ext
            
            dest_path = os.path.join(IMAGE_DIR, safe_filename)

            # 2. Copy Image
            shutil.copy(self.source_path, dest_path)

            # 3. Update JSON
            if os.path.exists(DB_FILE) and os.path.getsize(DB_FILE) > 0:
                with open(DB_FILE, 'r') as f:
                    try:
                        data = json.load(f)
                    except json.JSONDecodeError:
                        data = []
            else:
                data = []

            new_entry = {
                "id": len(data) + 1,
                "url": f"images/{safe_filename}",
                "title": title,
                "location": location,
                "description": desc,
                "date_added": datetime.now().strftime("%Y-%m-%d")
            }

            data.insert(0, new_entry)

            with open(DB_FILE, 'w') as f:
                json.dump(data, f, indent=4)

            # 4. Success & Reset
            messagebox.showinfo("Success", "Portfolio updated successfully!")
            self.reset_form()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save:\n{e}")

    def reset_form(self):
        self.source_path = None
        self.title_var.set("")
        self.location_var.set("")
        self.desc_var.set("")
        self.status_var.set("Waiting for image...")
        
        # Reset visual styles
        self.drop_label.config(text="📂 DRAG IMAGE HERE\n(or click to browse)", bg="#dddddd", fg="#555555")
        self.drop_frame.config(bg="#dddddd")
        self.save_btn.config(state="disabled", bg="#2ecc71")

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = PortfolioUploader(root)
    root.mainloop()
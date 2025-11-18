import tkinter as tk
from tkinter import ttk, messagebox
import json
import threading
import os

STATUS_FILE = "status.json"
DEFAULT_STATEN = {"woonkamer_licht": True, "keuken_licht": True, "slaapkamer_licht": False, "gas": True}

def load_status():
    if os.path.exists(STATUS_FILE):
        try:
            with open(STATUS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return DEFAULT_STATEN.copy()
    return DEFAULT_STATEN.copy()

def save_status(staten):
    with open(STATUS_FILE, "w") as f:
        json.dump(staten, f)

class ColorToggle(tk.Frame):
    def __init__(self, master, apparaat, status_var, toggle_cmd, schedule_cmd, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.apparaat = apparaat
        self.status_var = status_var
        self.toggle_cmd = toggle_cmd
        self.schedule_cmd = schedule_cmd
        self.build()

    def build(self):
        self.configure(padx=6, pady=6, relief="ridge", bd=1, background="#fafafa")
        # Icon + name
        icon = "💡" if "licht" in self.apparaat else "🔥" if "gas" in self.apparaat else "🔌"
        name_lbl = tk.Label(self, text=f"{icon}  {self.apparaat.replace('_',' ')}", anchor="w",
                            font=("Segoe UI", 11, "bold"), background="#fafafa")
        name_lbl.grid(row=0, column=0, sticky="w")

        # Status pill
        self.pill = tk.Label(self, textvariable=self.status_var, width=8,
                             font=("Segoe UI", 10, "bold"), anchor="center")
        self._style_pill()
        self.pill.grid(row=0, column=1, padx=(8,0))

        # Buttons
        btn_frame = tk.Frame(self, background="#fafafa")
        btn_frame.grid(row=0, column=2, sticky="e", padx=(12,0))

        toggle_btn = ttk.Button(btn_frame, text="Toggle", command=self.toggle_cmd, width=8)
        toggle_btn.pack(side="left", padx=(0,6))

        schedule_btn = ttk.Button(btn_frame, text="Plan uit", command=self.schedule_cmd, width=8)
        schedule_btn.pack(side="left")

    def _style_pill(self):
        txt = self.status_var.get()
        if txt == "aan":
            bg = "#16a085"      # groen
            fg = "white"
        else:
            bg = "#7f8c8d"      # grijs
            fg = "white"
        self.pill.configure(background=bg, foreground=fg, bd=0, relief="flat", padx=6, pady=2)

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Energiebeheer")
        self.configure(background="#f0f4f8")
        self.geometry("640x420")
        self.resizable(False, False)
        self.staten = load_status()
        self.timer_refs = {}
        self.style = ttk.Style(self)
        self._setup_style()
        self.build_ui()

    def _setup_style(self):
        self.style.theme_use("clam")
        self.style.configure("TButton", font=("Segoe UI", 10), padding=6)
        self.style.map("TButton",
                       foreground=[('pressed', 'white'), ('active', 'white')],
                       background=[('pressed', '#2980b9'), ('active', '#3498db')])
        self.default_font = ("Segoe UI", 10)

    def build_ui(self):
        header = tk.Frame(self, background="#2c3e50", height=72)
        header.pack(fill="x")
        tk.Label(header, text="Energiebeheer", bg="#2c3e50", fg="white",
                 font=("Segoe UI", 16, "bold")).pack(side="left", padx=16, pady=14)
        tk.Label(header, text="Slim en kleurrijk", bg="#2c3e50", fg="#dfe6ee",
                 font=("Segoe UI", 10)).pack(side="left", padx=(8,0), pady=18)

        content = tk.Frame(self, background="#f0f4f8")
        content.pack(fill="both", expand=True, padx=14, pady=12)

        # Left: apparaten list
        left = tk.Frame(content, background="#f0f4f8")
        left.pack(side="left", fill="both", expand=True)

        tk.Label(left, text="Apparaten", bg="#f0f4f8", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0,8))

        self.device_frames = {}
        for apparaat in self.staten.keys():
            status_var = tk.StringVar(value="aan" if self.staten[apparaat] else "uit")
            def make_toggle(a=apparaat, sv=status_var):
                def toggle():
                    self.staten[a] = not self.staten[a]
                    sv.set("aan" if self.staten[a] else "uit")
                    save_status(self.staten)
                    self.device_frames[a]._style_pill()
                return toggle

            def make_schedule(a=apparaat, sv=status_var):
                def schedule():
                    try:
                        sec = int(self.timer_entry.get())
                        if sec <= 0:
                            raise ValueError
                    except Exception:
                        messagebox.showerror("Fout", "Voer een positief geheel aantal seconden in")
                        return
                    if a in self.timer_refs:
                        self.timer_refs[a].cancel()
                    t = threading.Timer(sec, lambda: self.auto_off(a))
                    self.timer_refs[a] = t
                    t.start()
                    messagebox.showinfo("Gepland", f"{a} wordt over {sec} seconden uitgezet")
                return schedule

            frame = ColorToggle(left, apparaat, status_var, make_toggle(), make_schedule())
            frame.pack(fill="x", pady=6)
            self.device_frames[apparaat] = frame

        # Right: controls / info
        right = tk.Frame(content, background="#f0f4f8", width=220)
        right.pack(side="right", fill="y", padx=(12,0))

        tk.Label(right, text="Timer (s)", bg="#f0f4f8", font=self.default_font).pack(anchor="w")
        self.timer_entry = ttk.Entry(right, width=12)
        self.timer_entry.pack(anchor="w", pady=(6,10))

        ttk.Separator(right, orient="horizontal").pack(fill="x", pady=8)

        tk.Label(right, text="Acties", bg="#f0f4f8", font=self.default_font).pack(anchor="w", pady=(6,4))
        ttk.Button(right, text="Alles uit", command=self.turn_off_all).pack(fill="x", pady=4)
        ttk.Button(right, text="Alles aan", command=self.turn_on_all).pack(fill="x", pady=4)
        ttk.Button(right, text="Opslaan status", command=lambda: save_status(self.staten)).pack(fill="x", pady=14)
        ttk.Button(right, text="Sluiten", command=self.quit_and_save).pack(fill="x", pady=(20,0))

        # Footer
        footer = tk.Frame(self, background="#ecf0f1", height=28)
        footer.pack(fill="x", side="bottom")
        tk.Label(footer, text="Status wordt lokaal opgeslagen in status.json", bg="#ecf0f1",
                 font=("Segoe UI", 9)).pack(side="left", padx=10, pady=4)

    def auto_off(self, apparaat):
        self.staten[apparaat] = False
        save_status(self.staten)
        self.device_frames[apparaat].status_var.set("uit")
        self.device_frames[apparaat]._style_pill()
        messagebox.showinfo("Automatisch uitgezet", f"{apparaat} is nu uitgezet")

    def turn_off_all(self):
        for a in list(self.staten.keys()):
            self.staten[a] = False
            self.device_frames[a].status_var.set("uit")
            self.device_frames[a]._style_pill()
        save_status(self.staten)
        messagebox.showinfo("Klaar", "Alle apparaten zijn uitgezet")

    def turn_on_all(self):
        for a in list(self.staten.keys()):
            self.staten[a] = True
            self.device_frames[a].status_var.set("aan")
            self.device_frames[a]._style_pill()
        save_status(self.staten)
        messagebox.showinfo("Klaar", "Alle apparaten zijn aangezet")

    def quit_and_save(self):
        for t in self.timer_refs.values():
            try:
                t.cancel()
            except Exception:
                pass
        save_status(self.staten)
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()
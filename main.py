import os
import sys
import threading
import time
import webbrowser
import customtkinter as ctk
from pynput.keyboard import Key, Listener
from pynput.mouse import Button, Controller


def get_resource_path(relative_path):
    """Ottiene il percorso assoluto della risorsa (funziona sia in dev che in .exe)"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# Configurazione tema CustomTkinter
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class AutoClickerApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Simple Autoclicker")
        self.geometry("460x550")
        self.resizable(False, False)

        # Fix Icona Windows
        icon_path = get_resource_path("icona.ico")
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
                if sys.platform.startswith("win"):
                    import ctypes

                    myappid = "aken.simpleautoclicker.gui.1.1.0"
                    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                        myappid
                    )
                    self.after(200, lambda: self.iconbitmap(icon_path))
            except Exception:
                pass

        # Variabili di stato (Default impostato a 1 CPS)
        self.mouse = Controller()
        self.is_clicking = False
        self.cps = 1.0

        # --- GUI INTERFACE ---

        # Title / Header
        self.title_label = ctk.CTkLabel(
            self,
            text="Simple Autoclicker",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        self.title_label.pack(pady=(15, 2))

        self.author_label = ctk.CTkLabel(
            self, text="V 1.1.0 by Aken", text_color="gray"
        )
        self.author_label.pack(pady=(0, 10))

        # Preset Buttons Section
        self.preset_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.preset_frame.pack(pady=10, padx=20, fill="x")

        self.preset_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="equal")

        # Slow (Blu)
        self.btn_slow = ctk.CTkButton(
            self.preset_frame,
            text="Slow\n(1 CPS)",
            fg_color="#007bff",
            hover_color="#0056b3",
            font=ctk.CTkFont(weight="bold"),
            command=lambda: self.set_cps(1),
        )
        self.btn_slow.grid(row=0, column=0, padx=4, pady=5, sticky="ew")

        # Medium (Blu)
        self.btn_med = ctk.CTkButton(
            self.preset_frame,
            text="Medium\n(20 CPS)",
            fg_color="#007bff",
            hover_color="#0056b3",
            font=ctk.CTkFont(weight="bold"),
            command=lambda: self.set_cps(20),
        )
        self.btn_med.grid(row=0, column=1, padx=4, pady=5, sticky="ew")

        # Fast (Blu)
        self.btn_fast = ctk.CTkButton(
            self.preset_frame,
            text="Fast\n(50 CPS)",
            fg_color="#007bff",
            hover_color="#0056b3",
            font=ctk.CTkFont(weight="bold"),
            command=lambda: self.set_cps(50),
        )
        self.btn_fast.grid(row=0, column=2, padx=4, pady=5, sticky="ew")

        # Turbo (Rosso)
        self.btn_turbo = ctk.CTkButton(
            self.preset_frame,
            text="Turbo (5000 CPS)",
            fg_color="#dc3545",
            hover_color="#c82333",
            font=ctk.CTkFont(weight="bold"),
            command=lambda: self.set_cps(5000),
        )
        self.btn_turbo.grid(
            row=1, column=0, columnspan=3, padx=4, pady=(5, 10), sticky="ew"
        )

        # Custom Slider & Entry Section
        self.cps_label = ctk.CTkLabel(
            self,
            text="Speed (CPS):",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.cps_label.pack(pady=(15, 5))

        # Frame per affiancare Slider ed Entry
        self.controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.controls_frame.pack(pady=5, padx=30, fill="x")

        self.slider = ctk.CTkSlider(
            self.controls_frame,
            from_=1,
            to=10000,
            number_of_steps=9999,
            command=self.update_cps_from_slider,
        )
        self.slider.set(self.cps)
        self.slider.pack(side="left", fill="x", expand=True, padx=(0, 10))

        # Entry per inserimento manuale CPS
        self.cps_entry = ctk.CTkEntry(
            self.controls_frame,
            width=70,
            font=ctk.CTkFont(size=13, weight="bold"),
            justify="center",
        )
        self.cps_entry.insert(0, str(int(self.cps)))
        self.cps_entry.pack(side="right")
        self.cps_entry.bind("<KeyRelease>", self.update_cps_from_entry)

        # Start / Stop Button
        self.start_btn = ctk.CTkButton(
            self,
            text="START (F6)",
            fg_color="#28a745",
            hover_color="#218838",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=45,
            command=self.toggle_clicking,
        )
        self.start_btn.pack(pady=20, padx=30, fill="x")

        # Status Label
        self.status_label = ctk.CTkLabel(
            self, text="Status: Idle", text_color="gray"
        )
        self.status_label.pack(pady=(5, 2))

        # Warning Label
        self.warning_label = ctk.CTkLabel(
            self,
            text="WARNING: Increasing CPS too much puts a heavy load on the CPU",
            text_color="gray",
        )
        self.warning_label.pack(pady=(2, 5))

        # Footer (GitHub Link)
        self.footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.footer_frame.pack(side="bottom", fill="x", padx=15, pady=15)

        self.github_btn = ctk.CTkButton(
            self.footer_frame,
            text="🔗 GitHub Profile",
            width=120,
            fg_color="transparent",
            border_width=1,
            text_color="#D3D3D3",
            command=self.open_github,
        )
        self.github_btn.pack(side="left")

        # Global Hotkey Listener Initialization
        self.start_keyboard_listener()

    def update_cps_from_slider(self, value):
        val = int(float(value))
        self.cps = float(val)
        self.cps_entry.delete(0, "end")
        self.cps_entry.insert(0, str(val))

    def update_cps_from_entry(self, event=None):
        val_str = self.cps_entry.get().strip()
        if val_str.isdigit():
            val = int(val_str)
            if val < 1:
                val = 1
            elif val > 10000:
                val = 10000
            self.cps = float(val)
            self.slider.set(self.cps)

    def set_cps(self, value):
        self.cps = float(value)
        self.slider.set(value)
        self.cps_entry.delete(0, "end")
        self.cps_entry.insert(0, str(int(value)))

    def toggle_clicking(self):
        self.is_clicking = not self.is_clicking
        if self.is_clicking:
            self.start_btn.configure(
                text="STOP (F6)", fg_color="#dc3545", hover_color="#c82333"
            )
            self.status_label.configure(
                text="Status: RUNNING...", text_color="#28a745"
            )
            threading.Thread(target=self.click_loop, daemon=True).start()
        else:
            self.start_btn.configure(
                text="START (F6)", fg_color="#28a745", hover_color="#218838"
            )
            self.status_label.configure(
                text="Status: Idle", text_color="gray"
            )

    def click_loop(self):
        while self.is_clicking:
            self.mouse.click(Button.left)
            time.sleep(1.0 / self.cps)

    def open_github(self):
        webbrowser.open("https://github.com/Ak3nyke")

    def start_keyboard_listener(self):

        def on_press(key):
            if key == Key.f6:
                self.toggle_clicking()

        listener = Listener(on_press=on_press)
        listener.daemon = True
        listener.start()


if __name__ == "__main__":
    app = AutoClickerApp()
    app.mainloop()
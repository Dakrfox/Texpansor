import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import keyboard
import pyperclip
import threading
import time
import sys
import os
import ctypes
import winreg
import json
 
APP_NAME = "TEXPANSOR"
CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".texpansor_config.json")
 
DEFAULT_TRIGGERS = {
    "--prompt": """# Tarea
[Acción principal]
 
# Contexto
[Trasfondo de la solicitud]
 
# Formato
[Estructura deseada, ej: Tabla, Código]
 
# Estilo
[Tono o rol, ej: Técnico, Empático]
""",
}
 
def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {"triggers": DEFAULT_TRIGGERS}
 
def save_config(config):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error al guardar config: {e}")
 
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False
 
def add_to_startup():
    file_path = os.path.realpath(sys.argv[0])
    command = f'"{file_path}" --boot'
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r"Software\Microsoft\Windows\CurrentVersion\Run",
                             0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, command)
        winreg.CloseKey(key)
    except Exception as e:
        print(f"Error al agregar al inicio: {e}")
 
def replace_text(trigger, template):
    time.sleep(0.1)
    for _ in range(len(trigger)):
        keyboard.send('backspace')
    time.sleep(0.05)
    original_clipboard = pyperclip.paste()
    pyperclip.copy(template)
    keyboard.send('ctrl+v')
    time.sleep(0.1)
    pyperclip.copy(original_clipboard)
 
def start_keyboard_listener(get_triggers_fn):
    buffer = ""
 
    def on_key_event(event):
        nonlocal buffer
        if event.event_type != keyboard.KEY_DOWN:
            return
        char = event.name
        if char == 'space':
            char = ' '
        elif len(char) > 1:
            buffer = ""
            return
        buffer += char
        triggers = get_triggers_fn()
        for trigger, template in triggers.items():
            if buffer.endswith(trigger):
                matched_trigger = trigger
                matched_template = template
                buffer = ""
                threading.Thread(
                    target=replace_text,
                    args=(matched_trigger, matched_template),
                    daemon=True
                ).start()
                return
        max_len = max((len(t) for t in triggers), default=20) * 2
        if len(buffer) > max_len:
            buffer = buffer[-max_len:]
 
    keyboard.hook(on_key_event)
    keyboard.wait()
 
BG         = "#0f0f0f"
BG2        = "#1a1a1a"
BG3        = "#242424"
ACCENT     = "#00e5a0"
ACCENT2    = "#00b37a"
FG         = "#f0f0f0"
FG2        = "#888888"
DANGER     = "#e05555"
FONT_TITLE = ("Courier New", 20, "bold")
FONT_MONO  = ("Courier New", 10)
FONT_SMALL = ("Segoe UI", 9)
 
class TexpansorApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_NAME)
        self.root.geometry("620x580")
        self.root.resizable(False, False)
        self.root.configure(bg=BG)
 
        self.config = load_config()
        self.selected_trigger = None
 
        self._build_ui()
        self._refresh_list()
 
        listener_thread = threading.Thread(
            target=start_keyboard_listener,
            args=(lambda: self.config["triggers"],),
            daemon=True
        )
        listener_thread.start()
 
    def _build_ui(self):
        # ── Header ──
        header = tk.Frame(self.root, bg=BG, pady=16)
        header.pack(fill="x", padx=24)
 
        tk.Label(header, text="TEXPANSOR", font=FONT_TITLE,
                 fg=ACCENT, bg=BG).pack(side="left")
 
        status_frame = tk.Frame(header, bg=BG)
        status_frame.pack(side="right", pady=4)
        self.status_dot = tk.Label(status_frame, text="●", font=("Segoe UI", 14),
                                   fg=ACCENT, bg=BG)
        self.status_dot.pack(side="left")
        tk.Label(status_frame, text=" activo", font=FONT_SMALL,
                 fg=FG2, bg=BG).pack(side="left")
 
        tk.Frame(self.root, bg=BG3, height=1).pack(fill="x", padx=24)
 
        # ── Footer (se empaca ANTES del main para que siempre sea visible) ──
        footer = tk.Frame(self.root, bg=BG, pady=10)
        footer.pack(side="bottom", fill="x", padx=24, pady=(0, 12))
 
        self._btn(footer, "Ocultar", self.root.iconify, BG3).pack(side="left")
 
        self.cancel_btn = self._btn(footer, "✕ Cancelar", self._cancel_new, DANGER)
        # No se hace .pack() aquí — aparece solo en modo nuevo
 
        self.save_btn = self._btn(footer, "Guardar cambios", self._save_trigger, ACCENT)
        self.save_btn.pack(side="right")
 
        # ── Main area ──
        main = tk.Frame(self.root, bg=BG)
        main.pack(fill="both", expand=True, padx=24, pady=(16, 0))
 
        # Left: lista de triggers
        left = tk.Frame(main, bg=BG)
        left.pack(side="left", fill="y", padx=(0, 16))
 
        tk.Label(left, text="TRIGGERS", font=("Segoe UI", 9, "bold"),
                 fg=FG2, bg=BG).pack(anchor="w", pady=(0, 6))
 
        list_frame = tk.Frame(left, bg=BG2, highlightthickness=1, highlightbackground=BG3)
        list_frame.pack(fill="y", expand=True)
 
        scrollbar = tk.Scrollbar(list_frame, bg=BG2, troughcolor=BG2,
                                 relief="flat", highlightthickness=0)
        scrollbar.pack(side="right", fill="y")
 
        self.trigger_listbox = tk.Listbox(
            list_frame, width=18, bg=BG2, fg=FG,
            selectbackground=ACCENT, selectforeground="#000000",
            font=FONT_MONO, bd=0, relief="flat",
            activestyle="none", highlightthickness=0,
            yscrollcommand=scrollbar.set
        )
        self.trigger_listbox.pack(side="left", fill="both", expand=True, padx=1)
        scrollbar.config(command=self.trigger_listbox.yview)
        self.trigger_listbox.bind("<<ListboxSelect>>", self._on_select)
 
        btn_row = tk.Frame(left, bg=BG)
        btn_row.pack(fill="x", pady=(8, 0))
        self._btn(btn_row, "+ Nuevo", self._new_trigger, ACCENT).pack(side="left")
        self._btn(btn_row, "🗑", self._delete_trigger, DANGER, width=3).pack(side="right")
 
        # Right: editor
        right = tk.Frame(main, bg=BG)
        right.pack(side="left", fill="both", expand=True)
        right.grid_rowconfigure(3, weight=1)
        right.grid_columnconfigure(0, weight=1)
 
        tk.Label(right, text="TRIGGER", font=("Segoe UI", 9, "bold"),
                 fg=FG2, bg=BG).grid(row=0, column=0, sticky="w", pady=(0, 4))
 
        self.trigger_entry = tk.Entry(
            right, font=FONT_MONO, bg=BG2, fg=ACCENT,
            insertbackground=ACCENT, relief="flat", bd=8,
            highlightthickness=1, highlightbackground=BG3, highlightcolor=ACCENT
        )
        self.trigger_entry.grid(row=1, column=0, sticky="ew", pady=(0, 12))
 
        tk.Label(right, text="TEXTO A EXPANDIR", font=("Segoe UI", 9, "bold"),
                 fg=FG2, bg=BG).grid(row=2, column=0, sticky="w", pady=(0, 4))
 
        text_frame = tk.Frame(right, bg=BG2, highlightthickness=1, highlightbackground=BG3)
        text_frame.grid(row=3, column=0, sticky="nsew")
 
        self.template_text = tk.Text(
            text_frame, font=FONT_MONO, bg=BG2, fg=FG,
            insertbackground=ACCENT, relief="flat", bd=8,
            wrap="word", undo=True, highlightthickness=0
        )
        self.template_text.pack(fill="both", expand=True)
 
    def _btn(self, parent, text, cmd, color, width=None):
        kwargs = dict(
            text=text, command=cmd,
            bg=color, fg="#000000" if color == ACCENT else FG,
            font=FONT_SMALL, relief="flat", bd=0,
            padx=12, pady=6, cursor="hand2",
            activebackground=ACCENT2 if color == ACCENT else BG3,
            activeforeground="#000000" if color == ACCENT else FG
        )
        if width:
            kwargs["width"] = width
        return tk.Button(parent, **kwargs)
 
    def _refresh_list(self):
        self.trigger_listbox.delete(0, "end")
        for t in self.config["triggers"]:
            self.trigger_listbox.insert("end", f" {t}")
 
    def _on_select(self, event):
        sel = self.trigger_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        trigger = list(self.config["triggers"].keys())[idx]
        self.selected_trigger = trigger
        self.trigger_entry.delete(0, "end")
        self.trigger_entry.insert(0, trigger)
        self.template_text.delete("1.0", "end")
        self.template_text.insert("1.0", self.config["triggers"][trigger])
        self._set_new_mode(False)
 
    def _new_trigger(self):
        self.selected_trigger = None
        self.trigger_listbox.selection_clear(0, "end")
        self.trigger_entry.delete(0, "end")
        self.trigger_entry.insert(0, "--nuevo")
        self.template_text.delete("1.0", "end")
        self.template_text.insert("1.0", "Tu texto aquí...")
        self.trigger_entry.focus()
        self._set_new_mode(True)
 
    def _set_new_mode(self, active):
        if active:
            self.save_btn.config(text="✓ Crear trigger")
            self.cancel_btn.pack(side="right", padx=(0, 6))
        else:
            self.save_btn.config(text="Guardar cambios")
            self.cancel_btn.pack_forget()
 
    def _cancel_new(self):
        self._set_new_mode(False)
        self.trigger_entry.delete(0, "end")
        self.template_text.delete("1.0", "end")
        self.selected_trigger = None
 
    def _save_trigger(self):
        trigger = self.trigger_entry.get().strip()
        template = self.template_text.get("1.0", "end-1c")
        if not trigger:
            messagebox.showwarning("Campo vacío", "El trigger no puede estar vacío.")
            return
        if self.selected_trigger and self.selected_trigger != trigger:
            del self.config["triggers"][self.selected_trigger]
        self.config["triggers"][trigger] = template
        self.selected_trigger = trigger
        save_config(self.config)
        self._refresh_list()
        keys = list(self.config["triggers"].keys())
        if trigger in keys:
            idx = keys.index(trigger)
            self.trigger_listbox.selection_clear(0, "end")
            self.trigger_listbox.selection_set(idx)
            self.trigger_listbox.see(idx)
        self._set_new_mode(False)
        self._flash_status()
 
    def _delete_trigger(self):
        if not self.selected_trigger:
            return
        if not messagebox.askyesno("Eliminar", f"¿Eliminar '{self.selected_trigger}'?"):
            return
        del self.config["triggers"][self.selected_trigger]
        self.selected_trigger = None
        self.trigger_entry.delete(0, "end")
        self.template_text.delete("1.0", "end")
        save_config(self.config)
        self._refresh_list()
 
    def _flash_status(self):
        self.status_dot.config(fg="#ffffff")
        self.root.after(200, lambda: self.status_dot.config(fg=ACCENT))
 
 
def show_boot_notification():
    toast = tk.Tk()
    toast.overrideredirect(True)
    toast.geometry("300x50+10+10")
    toast.configure(bg=ACCENT)
    msg = tk.Label(toast, text=f"{APP_NAME} ejecutándose en segundo plano",
                   font=("Segoe UI", 10, "bold"), fg="#000000", bg=ACCENT)
    msg.pack(expand=True, fill="both")
    toast.after(1500, toast.destroy)
    toast.mainloop()
 
 
if __name__ == "__main__":
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()
 
    add_to_startup()
 
    if "--boot" in sys.argv:
        show_boot_notification()
        root = tk.Tk()
        app = TexpansorApp(root)
        root.iconify()
        root.mainloop()
    else:
        root = tk.Tk()
        app = TexpansorApp(root)
        root.mainloop()
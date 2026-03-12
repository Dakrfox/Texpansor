# TEXPANSOR

A lightweight Windows desktop utility that expands short text triggers into full templates — instantly, in any application.

---

## What It Does

TEXPANSOR runs silently in the background and listens for trigger words you type. When it detects one, it automatically deletes the trigger and replaces it with a pre-configured block of text — in any app, any text field, anywhere on your system.

**Example:** Type `--prompt` in a chat window, a browser, a code editor, or Notepad — and it instantly expands into a structured prompt template:

```
# Tarea
[Acción principal]

# Contexto
[Trasfondo de la solicitud]

# Formato
[Estructura deseada, ej: Tabla, Código]

# Estilo
[Tono o rol, ej: Técnico, Empático]
```

You can create as many triggers as you want, each expanding into its own custom text.

---

## Features

- **Multi-trigger support** — define unlimited trigger/template pairs
- **Live listener** — all triggers are active simultaneously with no restart needed
- **Persistent config** — triggers are saved to `~/.texpansor_config.json` and survive restarts
- **Works anywhere** — expands text in any application (browsers, editors, chat apps, IDEs)
- **Auto-start** — registers itself to launch with Windows on first run
- **Minimal UI** — dark interface with trigger list, inline editor, and one-click hide

---

## Requirements

- Windows 10 or 11
- Python 3.8+
- The following Python packages:

```
keyboard
pyperclip
```

Install them with:

```bash
pip install keyboard pyperclip
```

> `tkinter` is included with standard Python installations and does not need to be installed separately.

---

## How to Run

1. Clone or download this repository.
2. Install the dependencies (see above).
3. Run the script:

```bash
python app.py
```

> **Important:** Windows will prompt you for administrator privileges. This is required for the `keyboard` library to intercept global keystrokes across all applications. The app does not use this access for anything other than detecting your configured triggers.

On first launch, the app will also register itself in the Windows startup registry so it starts automatically with your system.

---

## Using the App

### Adding a trigger

1. Click **+ Nuevo** in the left panel.
2. Type your trigger word in the **TRIGGER** field (e.g. `--email`, `--firma`, `--sql`).
3. Type the expanded text in the **TEXTO A EXPANDIR** field.
4. Click **✓ Crear trigger** to save.

### Editing a trigger

1. Click any trigger in the left list to select it.
2. Edit the trigger name or text as needed.
3. Click **Guardar cambios** to save.

> If you rename a trigger, the old name is automatically removed.

### Deleting a trigger

Select a trigger from the list and click the **🗑** button. You will be asked to confirm.

### Hiding the app

Click **Ocultar** to minimize TEXPANSOR to the taskbar. All triggers remain active while hidden.

---

## How the Text Expansion Works

TEXPANSOR uses `keyboard.hook()` to listen to every keystroke globally. It builds a rolling buffer of recent characters and checks whether the buffer ends with any of your configured triggers. When a match is found:

1. It sends `Backspace` once per character in the trigger to erase it.
2. It copies your template to the clipboard.
3. It simulates `Ctrl+V` to paste the expanded text.
4. It restores the original clipboard content.

This approach is fully local — no data is sent anywhere.

---

## Config File

Triggers are stored in:

```
C:\Users\<YourUser>\.texpansor_config.json
```

You can edit this file manually if needed. The format is:

```json
{
  "triggers": {
    "--prompt": "# Tarea\n...",
    "--firma": "Saludos,\nTu Nombre"
  }
}
```

---

## Auto-Start

On first run, TEXPANSOR registers the following registry key:

```
HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run\TEXPANSOR
```

When launched automatically at boot, the app starts minimized and shows a brief notification in the top-left corner of your screen.

To disable auto-start, remove the `TEXPANSOR` entry from the registry using `regedit` or the Task Manager startup tab.

---

## Troubleshooting

**Trigger is not expanding:**
- Make sure you accepted the administrator prompt when launching.
- Open a terminal and run `python texpansor.py` directly to see any error output.
- Add a `print` statement inside `on_key_event` to verify keystrokes are being received.

**Text expands in the wrong place:**
- Increase the `time.sleep(0.1)` delay in `replace_text()` if your system is slow to process clipboard events.

**App won't start:**
- Confirm `keyboard` and `pyperclip` are installed: `pip install keyboard pyperclip`
- Confirm you are running Python 3.8 or newer: `python --version`

# Build via GitHub Actions\nimport json
import os
import sys
import threading
import time
import webbrowser
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

import requests
import serial
from serial.tools import list_ports

APP_NAME = "Connector Micro:bit → ThingSpeak v5.1"
APP_VERSION = "5.1.0"
PROJECT_NAME = "Estació Meteorològica en Xarxa"
PROJECT_ORIGINAL = "Anton Nin Nin i Paula Pacho Ruiz"
AUTHOR = "Ignasi Sánchez Rodríguez"
FRAMEWORK = "Mentoria Digital 4.0"
LICENSE_NAME = "PolyForm Noncommercial 1.0.0"
LICENSE_URL = "https://polyformproject.org/licenses/noncommercial/1.0.0"

MENTORIES_LOGO_PNG = (
    "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"
)
CONFIG_FILE = "microbit_thingspeak_config.json"
BAUD = 115200
DEFAULT_INTERVAL = 15

def app_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

CONFIG_PATH = os.path.join(app_dir(), CONFIG_FILE)

def load_config():
    cfg = {"api_key": "", "interval": DEFAULT_INTERVAL}
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            cfg.update(json.load(f))
    except Exception:
        pass
    return cfg

def save_config(cfg):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)

def find_microbit_port():
    ports = list(list_ports.comports())
    keywords = ("micro:bit", "microbit", "cmsis-dap", "mbed")
    for p in ports:
        txt = " ".join(str(x or "") for x in (
            p.description, p.manufacturer, p.product, p.hwid
        )).lower()
        if any(k in txt for k in keywords):
            return p.device
    if len(ports) == 1:
        return ports[0].device
    return None

class GatewayApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_NAME)
        self.root.geometry("650x350")
        self.root.resizable(False, False)

        self.cfg = load_config()
        self.stop_event = threading.Event()
        self.worker = None
        self.ser = None
        self.last_raw_response = ""
        self.last_sent_line = ""
        self.last_entry_id = ""

        frame = ttk.Frame(root, padding=18)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Micro:bit → ThingSpeak",
                  font=("Segoe UI", 17, "bold")).pack(anchor="w")
        ttk.Label(frame, text="Pont automàtic USB/Serial → Internet → ThingSpeak").pack(
            anchor="w", pady=(2, 16)
        )

        box = ttk.LabelFrame(frame, text="Estat", padding=12)
        box.pack(fill="x")

        self.status_var = tk.StringVar(value="Iniciant...")
        ttk.Label(box, textvariable=self.status_var,
                  font=("Segoe UI", 12, "bold")).pack(anchor="w")

        self.detail_var = tk.StringVar(value="Preparant...")
        ttk.Label(box, textvariable=self.detail_var, wraplength=500).pack(
            anchor="w", pady=(8, 0)
        )

        ttk.Separator(frame).pack(fill="x", pady=14)

        buttons = ttk.Frame(frame)
        buttons.pack(fill="x")
        ttk.Button(buttons, text="Reinicia pont", command=self.restart_gateway).pack(side="left")
        ttk.Button(buttons, text="Canvia API Key", command=self.change_api_key).pack(side="left", padx=8)
        ttk.Button(buttons, text="Debug", command=self.show_debug).pack(side="left")
        ttk.Button(buttons, text="ℹ Quant a", command=self.show_about).pack(side="left", padx=(8, 0))
        ttk.Button(buttons, text="Surt", command=self.on_close).pack(side="right")

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        if not self.cfg.get("api_key"):
            self.root.after(250, self.first_run_setup)
        else:
            self.root.after(400, self.start_gateway)

    def first_run_setup(self):
        key = simpledialog.askstring(
            APP_NAME,
            "Primera configuració.\n\nEnganxa la Write API Key del teu canal de ThingSpeak:",
            parent=self.root,
        )
        if not key:
            self.ui("Falta configurar ThingSpeak", "Prem 'Canvia API Key' per configurar-lo.")
            return
        self.cfg["api_key"] = key.strip()
        self.cfg["interval"] = max(DEFAULT_INTERVAL, int(self.cfg.get("interval", DEFAULT_INTERVAL)))
        save_config(self.cfg)
        self.ui("Configuració guardada", "Buscant la micro:bit...")
        self.root.after(300, self.start_gateway)

    def change_api_key(self):
        key = simpledialog.askstring(
            APP_NAME,
            "Nova Write API Key de ThingSpeak:",
            initialvalue=self.cfg.get("api_key", ""),
            parent=self.root,
        )
        if key:
            self.cfg["api_key"] = key.strip()
            save_config(self.cfg)
            messagebox.showinfo(APP_NAME, "API Key guardada.")
            self.restart_gateway()


    def show_about(self):
        win = tk.Toplevel(self.root)
        win.title("Quant a")
        win.geometry("620x340")
        win.resizable(False, False)

        frm = ttk.Frame(win, padding=18)
        frm.pack(fill="both", expand=True)

        top = ttk.Frame(frm)
        top.pack(fill="x")

        titles = ttk.Frame(top)
        titles.pack(side="left", fill="x", expand=True)
        ttk.Label(titles, text="Connector Micro:bit → ThingSpeak",
                  font=("Segoe UI", 15, "bold")).pack(anchor="w")

        logo_source = tk.PhotoImage(data=MENTORIES_LOGO_PNG)
        logo_small = logo_source.subsample(2, 2)
        win._mentories_logo = (logo_source, logo_small)
        ttk.Label(top, image=logo_small).pack(side="right", anchor="ne", padx=(12, 0), pady=(2, 0))

        text = (
            f"Projecte: {PROJECT_NAME}\\n"
            f"Projecte original: {PROJECT_ORIGINAL}\\n"
            f"Connector desenvolupat per: {AUTHOR}\\n"
            f"{FRAMEWORK} · 2026\\n\\n"
            f"Versió: {APP_VERSION}\\n"
            f"Llicència: {LICENSE_NAME}\\n"
            f"{LICENSE_URL}"
        )
        ttk.Label(frm, text=text, justify="left", wraplength=570).pack(anchor="w", pady=(14, 0))

        actions = ttk.Frame(frm)
        actions.pack(fill="x", side="bottom", pady=(16, 0))
        ttk.Button(actions, text="Obre la llicència",
                   command=lambda: webbrowser.open(LICENSE_URL)).pack(side="left")
        ttk.Button(actions, text="Tanca", command=win.destroy).pack(side="right")

    def show_debug(self):
        win = tk.Toplevel(self.root)
        win.title("Debug")
        win.geometry("700x420")

        frm = ttk.Frame(win, padding=14)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text="Debug",
                  font=("Segoe UI", 14, "bold")).pack(anchor="w")
        ttk.Label(frm, text="Informació tècnica per a diagnosi i demostracions.").pack(
            anchor="w", pady=(2, 10)
        )

        info = tk.Text(frm, wrap="word", height=18)
        info.pack(fill="both", expand=True)

        port_text = self.ser.port if self.ser and getattr(self.ser, "is_open", False) else "No connectat"
        technical_text = (
            f"Port sèrie: {port_text}\n"
            f"Baud rate: {BAUD}\n"
            f"Interval mínim: {self.cfg.get('interval', DEFAULT_INTERVAL)} s\n\n"
            f"Última línia rebuda:\n{self.last_sent_line or '(cap)'}\n\n"
            f"Últim entry_id:\n{self.last_entry_id or '(cap)'}\n\n"
            f"Resposta completa de ThingSpeak (JSON):\n{self.last_raw_response or '(encara no hi ha resposta)'}"
        )
        info.insert("1.0", technical_text)
        info.configure(state="disabled")
        ttk.Button(frm, text="Tanca", command=win.destroy).pack(anchor="e", pady=(10, 0))

    def ui(self, status=None, detail=None):
        def apply():
            if status is not None:
                self.status_var.set(status)
            if detail is not None:
                self.detail_var.set(detail)
        self.root.after(0, apply)

    def restart_gateway(self):
        self.stop_gateway()
        self.root.after(600, self.start_gateway)

    def start_gateway(self):
        if self.worker and self.worker.is_alive():
            return
        if not self.cfg.get("api_key"):
            self.first_run_setup()
            return
        self.stop_event.clear()
        self.worker = threading.Thread(target=self.run_gateway, daemon=True)
        self.worker.start()

    def stop_gateway(self):
        self.stop_event.set()
        try:
            if self.ser and self.ser.is_open:
                self.ser.close()
        except Exception:
            pass

    def run_gateway(self):
        self.ui("Buscant micro:bit...", "Connecta la micro:bit per USB.")
        port = find_microbit_port()
        if not port:
            self.ui("No s'ha trobat cap micro:bit",
                    "Connecta-la per USB i prem 'Reinicia pont'.")
            return

        try:
            self.ser = serial.Serial(port, BAUD, timeout=1)
            time.sleep(1.5)
            self.ui("✅ Connectat", f"Micro:bit detectada a {port}. Esperant dades...")
        except Exception as e:
            self.ui("Error obrint la micro:bit", str(e))
            return

        last_send = 0.0
        interval = max(DEFAULT_INTERVAL, int(self.cfg.get("interval", DEFAULT_INTERVAL)))

        while not self.stop_event.is_set():
            try:
                raw = self.ser.readline()
                if not raw:
                    continue
                line = raw.decode("utf-8", errors="ignore").strip()
                if not line:
                    continue

                parts = [x.strip() for x in line.split(",")]
                if time.time() - last_send < interval:
                    continue

                start = 0
                if parts and not self.is_number(parts[0]):
                    start = 1
                values = parts[start:start + 8]
                if not values:
                    continue

                payload = {"api_key": self.cfg["api_key"]}
                for i, value in enumerate(values, start=1):
                    payload[f"field{i}"] = value

                r = requests.post(
                    "https://api.thingspeak.com/update.json",
                    data=payload,
                    timeout=10,
                )

                response_text = r.text.strip()
                self.last_raw_response = response_text
                self.last_sent_line = line

                if r.ok and response_text not in ("", "0"):
                    last_send = time.time()
                    try:
                        entry_id = str(r.json().get("entry_id", ""))
                    except Exception:
                        entry_id = response_text
                    self.last_entry_id = entry_id
                    shown = ", ".join(values)
                    detail = f"Últim valor enviat: {shown}"
                    if entry_id:
                        detail += f" · Entrada {entry_id}"
                    self.ui("✅ Enviant a ThingSpeak", detail)
                else:
                    self.ui("ThingSpeak ha rebutjat l'enviament",
                            "Revisa la connexió o la Write API Key.")

            except serial.SerialException:
                self.ui("Micro:bit desconnectada",
                        "Torna-la a connectar i prem 'Reinicia pont'.")
                break
            except requests.RequestException:
                self.ui("Sense connexió amb ThingSpeak",
                        "Comprova la connexió a Internet.")
                time.sleep(2)
            except Exception as e:
                self.ui("Error", str(e))
                time.sleep(2)

        try:
            if self.ser and self.ser.is_open:
                self.ser.close()
        except Exception:
            pass

    @staticmethod
    def is_number(text):
        try:
            float(text)
            return True
        except Exception:
            return False

    def on_close(self):
        self.stop_gateway()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    GatewayApp(root)
    root.mainloop()

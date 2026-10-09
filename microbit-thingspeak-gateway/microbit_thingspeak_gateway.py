# Build via GitHub Actions\nimport json
import os
import sys
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

import requests
import serial
from serial.tools import list_ports

APP_NAME = "Microbit → ThingSpeak Gateway v4"
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
        self.root.geometry("570x330")
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

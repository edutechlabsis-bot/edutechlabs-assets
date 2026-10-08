import asyncio
import json
import os
import sys
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

import requests
from bleak import BleakClient, BleakScanner

APP_NAME = "Microbit → ThingSpeak Bluetooth Gateway v3"
CONFIG_FILE = "microbit_thingspeak_bluetooth_config.json"
DEFAULT_INTERVAL = 15

UART_SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
UART_TX_UUID      = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"  # micro:bit -> PC (indicate)
UART_RX_UUID      = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"  # PC -> micro:bit (write)

def app_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

CONFIG_PATH = os.path.join(app_dir(), CONFIG_FILE)

def load_config():
    defaults = {"api_key": "", "interval": DEFAULT_INTERVAL, "name_filter": "micro:bit"}
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        defaults.update(data)
    except Exception:
        pass
    return defaults

def save_config(cfg):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)

class GatewayApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_NAME)
        self.root.geometry("650x360")
        self.root.resizable(False, False)

        self.cfg = load_config()
        self.stop_event = threading.Event()
        self.worker = None
        self.last_raw_response = ""
        self.last_sent_line = ""
        self.last_entry_id = ""
        self.current_device_name = ""
        self.last_send = 0.0

        frame = ttk.Frame(root, padding=18)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Micro:bit → ThingSpeak (Bluetooth)",
                  font=("Segoe UI", 16, "bold")).pack(anchor="w")
        ttk.Label(frame, text="Pont automàtic Bluetooth BLE → Internet → ThingSpeak").pack(anchor="w", pady=(2,16))

        box = ttk.LabelFrame(frame, text="Estat", padding=12)
        box.pack(fill="x")

        self.status_var = tk.StringVar(value="Iniciant...")
        ttk.Label(box, textvariable=self.status_var, font=("Segoe UI", 12, "bold")).pack(anchor="w")

        self.detail_var = tk.StringVar(value="Preparant...")
        ttk.Label(box, textvariable=self.detail_var, wraplength=590).pack(anchor="w", pady=(8,0))

        ttk.Separator(frame).pack(fill="x", pady=14)
        buttons = ttk.Frame(frame)
        buttons.pack(fill="x")
        ttk.Button(buttons, text="↻ Reinicia pont", command=self.restart_gateway).pack(side="left")
        ttk.Button(buttons, text="🔑 Canvia API Key", command=self.change_api_key).pack(side="left", padx=8)
        ttk.Button(buttons, text="🛰️ Canvia nom micro:bit", command=self.change_name_filter).pack(side="left")
        ttk.Button(buttons, text="Detalls tècnics", command=self.show_technical_details).pack(side="left", padx=8)
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
            parent=self.root
        )
        if not key:
            self.ui("Falta configurar ThingSpeak", "Prem «Canvia API Key» per configurar-lo.")
            return
        self.cfg["api_key"] = key.strip()
        save_config(self.cfg)
        self.ui("Configuració guardada", "Buscant micro:bit per Bluetooth...")
        self.root.after(300, self.start_gateway)

    def change_api_key(self):
        key = simpledialog.askstring(
            APP_NAME,
            "Nova Write API Key de ThingSpeak:",
            initialvalue=self.cfg.get("api_key",""),
            parent=self.root
        )
        if key:
            self.cfg["api_key"] = key.strip()
            save_config(self.cfg)
            messagebox.showinfo(APP_NAME, "API Key guardada.")
            self.restart_gateway()

    def change_name_filter(self):
        value = simpledialog.askstring(
            APP_NAME,
            "Part del nom Bluetooth a buscar (ex.: micro:bit):",
            initialvalue=self.cfg.get("name_filter","micro:bit"),
            parent=self.root
        )
        if value:
            self.cfg["name_filter"] = value.strip()
            save_config(self.cfg)
            messagebox.showinfo(APP_NAME, "Filtre de nom guardat.")
            self.restart_gateway()

    def show_technical_details(self):
        win = tk.Toplevel(self.root)
        win.title("Detalls tècnics")
        win.geometry("760x460")
        frm = ttk.Frame(win, padding=14)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text="Detalls tècnics", font=("Segoe UI",14,"bold")).pack(anchor="w")
        ttk.Label(frm, text="Informació avançada per a proves, diagnosi o demostracions.").pack(anchor="w", pady=(2,10))

        info = tk.Text(frm, wrap="word", height=20)
        info.pack(fill="both", expand=True)

        txt = (
            f"Versió de l'app: v3\n"
            f"Dispositiu Bluetooth: {self.current_device_name or '(no connectat)'}\n"
            f"Servei BLE esperat: {UART_SERVICE_UUID}\n"
            f"TX micro:bit → PC: {UART_TX_UUID}\n"
            f"RX PC → micro:bit: {UART_RX_UUID}\n"
            f"Filtre de nom: {self.cfg.get('name_filter','micro:bit')}\n"
            f"Interval mínim: {self.cfg.get('interval',DEFAULT_INTERVAL)} s\n\n"
            f"Última dada rebuda:\n{self.last_sent_line or '(cap)'}\n\n"
            f"Últim entry_id:\n{self.last_entry_id or '(cap)'}\n\n"
            f"Detall BLE / resposta ThingSpeak:\n{self.last_raw_response or '(encara no hi ha informació)'}"
        )

        info.insert("1.0", txt)
        info.configure(state="disabled")
        ttk.Button(frm, text="Tanca", command=win.destroy).pack(anchor="e", pady=(10,0))

    def ui(self, status=None, detail=None):
        def apply():
            if status is not None:
                self.status_var.set(status)
            if detail is not None:
                self.detail_var.set(detail)
        self.root.after(0, apply)

    def restart_gateway(self):
        self.stop_gateway()
        self.root.after(900, self.start_gateway)

    def start_gateway(self):
        if self.worker and self.worker.is_alive():
            return
        if not self.cfg.get("api_key"):
            self.first_run_setup()
            return
        self.stop_event.clear()
        self.worker = threading.Thread(target=self.run_async_thread, daemon=True)
        self.worker.start()

    def stop_gateway(self):
        self.stop_event.set()

    def run_async_thread(self):
        try:
            asyncio.run(self.ble_loop())
        except Exception as e:
            self.show_ble_exception(e)

    def show_ble_exception(self, e):
        msg = str(e)
        low = msg.lower()

        if "does not support notifications or indications" in low:
            self.ui(
                "Error de recepció Bluetooth",
                "La característica Bluetooth trobada no permet rebre dades. Prem «Detalls tècnics» per veure la informació BLE."
            )
        elif "not found" in low and "characteristic" in low:
            self.ui(
                "Característica Bluetooth no trobada",
                "La micro:bit està connectada, però no s'ha trobat el canal UART de recepció. Recarrega el programa MakeCode i torna a aparellar-la."
            )
        elif "not found" in low and "service" in low:
            self.ui(
                "Servei Bluetooth UART no trobat",
                "La micro:bit està connectada, però no exposa el servei UART. Comprova que el programa MakeCode inclogui «bluetooth servei uart»."
            )
        elif "bluetooth" in low and "adapter" in low:
            self.ui(
                "No hi ha cap adaptador Bluetooth",
                "Windows no detecta cap adaptador Bluetooth BLE disponible."
            )
        else:
            self.last_raw_response = msg
            self.ui(
                "Error de connexió Bluetooth",
                "No s'ha pogut completar la connexió. Prem «Detalls tècnics» per veure l'error."
            )

    async def ble_loop(self):
        self.ui("Buscant micro:bit...", "Activa Bluetooth a l'ordinador i encén la micro:bit.")

        try:
            devices = await BleakScanner.discover(timeout=8.0)
        except Exception as e:
            self.show_ble_exception(e)
            return

        name_filter = self.cfg.get("name_filter","micro:bit").lower()
        candidates = []
        for d in devices:
            name = (d.name or "").strip()
            if name_filter in name.lower() or "micro:bit" in name.lower():
                candidates.append(d)

        if not candidates:
            self.ui(
                "No s'ha trobat cap micro:bit",
                "Comprova que estigui aparellada amb Windows, engegada i a prop. Després prem «Reinicia pont»."
            )
            return

        # Prova candidats fins trobar-ne un que exposi el servei UART.
        last_error = None

        for device in candidates:
            if self.stop_event.is_set():
                return

            self.current_device_name = device.name or device.address
            self.ui("Connectant per Bluetooth...", f"Dispositiu: {self.current_device_name}")

            try:
                async with BleakClient(device) as client:
                    if not client.is_connected:
                        continue

                    uart_service = client.services.get_service(UART_SERVICE_UUID)
                    if uart_service is None:
                        last_error = "Dispositiu connectat però sense servei UART."
                        continue

                    def pot_rebre(ch):
                        props = {p.lower() for p in (ch.properties or [])}
                        return "notify" in props or "indicate" in props

                    tx_char = client.services.get_characteristic(UART_TX_UUID)

                    # Fallback robust dins del mateix servei UART.
                    if tx_char is None or not pot_rebre(tx_char):
                        tx_char = None
                        for char in uart_service.characteristics:
                            if pot_rebre(char):
                                tx_char = char
                                break

                    details = []
                    for char in uart_service.characteristics:
                        details.append(f"{char.uuid} · {', '.join(char.properties)}")
                    self.last_raw_response = "Característiques del servei UART:\n" + "\n".join(details)

                    if tx_char is None:
                        self.ui(
                            "No es pot rebre el UART",
                            "La micro:bit exposa UART, però cap característica permet rebre dades. Torna a carregar el programa MakeCode i torna-la a aparellar."
                        )
                        return

                    self.ui(
                        "✅ Connectat per Bluetooth",
                        f"Dispositiu: {self.current_device_name}. Esperant dades..."
                    )

                    self.last_raw_response += (
                        f"\n\nRecepció seleccionada: {tx_char.uuid}"
                        f"\nPropietats: {', '.join(tx_char.properties)}"
                    )

                    await client.start_notify(tx_char, self.notification_handler)

                    while not self.stop_event.is_set():
                        await asyncio.sleep(0.2)

                    try:
                        await client.stop_notify(tx_char)
                    except Exception:
                        pass

                    return

            except Exception as e:
                last_error = str(e)
                continue

        if last_error:
            self.last_raw_response = last_error
            self.show_ble_exception(Exception(last_error))
        else:
            self.ui(
                "No s'ha pogut connectar amb la micro:bit",
                "Comprova l'aparellament de Windows i prem «Reinicia pont»."
            )

    def notification_handler(self, sender, data: bytearray):
        try:
            text = bytes(data).decode("utf-8", errors="ignore").strip()
            if not text:
                return
            self.last_sent_line = text
            self.process_line(text)
        except Exception as e:
            self.last_raw_response = str(e)
            self.ui("Error processant les dades", "No s'ha pogut interpretar la dada rebuda per Bluetooth.")

    def process_line(self, line):
        try:
            now = time.time()
            interval = max(DEFAULT_INTERVAL, int(self.cfg.get("interval",DEFAULT_INTERVAL)))
            if now - self.last_send < interval:
                return

            parts = [x.strip() for x in line.split(",")]
            start = 0
            if parts and not self.is_number(parts[0]):
                start = 1

            values = parts[start:start+8]
            if not values:
                return

            payload = {"api_key": self.cfg["api_key"]}
            for i, value in enumerate(values, start=1):
                payload[f"field{i}"] = value

            r = requests.post(
                "https://api.thingspeak.com/update.json",
                data=payload,
                timeout=10
            )

            response_text = r.text.strip()
            self.last_raw_response = response_text

            if r.ok and response_text not in ("","0"):
                self.last_send = time.time()

                try:
                    entry_id = str(r.json().get("entry_id",""))
                except Exception:
                    entry_id = response_text

                self.last_entry_id = entry_id
                shown = ", ".join(values)

                detail = f"Últim valor enviat: {shown}"
                if entry_id:
                    detail += f" · Entrada {entry_id}"

                self.ui("✅ Enviant a ThingSpeak", detail)
            else:
                self.ui(
                    "⚠️ ThingSpeak ha rebutjat l'enviament",
                    "Revisa la connexió a Internet i la Write API Key."
                )

        except requests.RequestException:
            self.ui(
                "Sense connexió amb ThingSpeak",
                "Comprova la connexió a Internet."
            )
        except Exception as e:
            self.last_raw_response = str(e)
            self.ui(
                "Error enviant les dades",
                "No s'ha pogut enviar la dada a ThingSpeak. Prem «Detalls tècnics» per veure més informació."
            )

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

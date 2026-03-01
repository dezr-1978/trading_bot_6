import time
import threading
import tkinter as tk
from tkinter import ttk

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# === ТВОЇ МОДУЛІ (тут поки заглушки, щоб файл запускався) ===
try:
    from binance_api import BinanceAPI
except ImportError:
    class BinanceAPI:
        def get_price(self, symbol: str) -> float:
            # заглушка: повертаємо фейкову ціну
            return 65000.0

try:
    from strategy import TradingStrategy
except ImportError:
    class TradingStrategy:
        def generate_signal(self, price: float) -> str:
            # заглушка: просто HOLD
            return "HOLD"

try:
    from simulation import Simulator
except ImportError:
    class Simulator:
        def __init__(self):
            self.equity = 10000.0

        def process_signal(self, signal: str, price: float):
            # заглушка: нічого не робимо
            pass

MODE = "SIMULATION"  # SIMULATION / LIVE


class TradingApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("AI Trading Terminal")

        # --- ядро бота ---
        self.api = BinanceAPI()
        self.strategy = TradingStrategy()
        self.simulator = Simulator()

        self.running = False
        self.paused = False

        self.prices = []

        self._build_ui()
        self._schedule_ui_update()

    # ---------------- UI ----------------

    def _build_ui(self):
        # Верхня панель керування
        control_frame = ttk.Frame(self.root)
        control_frame.pack(fill="x", padx=5, pady=5)

        ttk.Button(control_frame, text="START", command=self.start_bot).pack(side="left", padx=2)
        ttk.Button(control_frame, text="PAUSE", command=self.pause_bot).pack(side="left", padx=2)
        ttk.Button(control_frame, text="STOP", command=self.stop_bot).pack(side="left", padx=2)

        # Статус
        self.status_label = ttk.Label(control_frame, text="Status: IDLE")
        self.status_label.pack(side="right")

        # Графік ціни
        fig = Figure(figsize=(7, 3))
        self.ax_price = fig.add_subplot(111)
        self.ax_price.set_title("Price")
        self.ax_price.set_xlabel("Tick")
        self.ax_price.set_ylabel("Price")

        self.canvas_price = FigureCanvasTkAgg(fig, master=self.root)
        self.canvas_price.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)

        # Логи
        log_frame = ttk.LabelFrame(self.root, text="Logs")
        log_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.log_box = tk.Text(log_frame, height=10)
        self.log_box.pack(fill="both", expand=True)

    # ------------- Керування ботом -------------

    def start_bot(self):
        if not self.running:
            self.running = True
            self.paused = False
            self._log("Bot started")
            threading.Thread(target=self._bot_loop, daemon=True).start()

    def pause_bot(self):
        if self.running:
            self.paused = not self.paused
            state = "paused" if self.paused else "resumed"
            self._log(f"Bot {state}")

    def stop_bot(self):
        if self.running:
            self.running = False
            self._log("Bot stopped")

    # ------------- Логіка бота в окремому потоці -------------

    def _bot_loop(self):
        symbol = "BTCUSDT"
        while self.running:
            if self.paused:
                time.sleep(0.5)
                continue

            # 1) Отримуємо ціну
            price = self.api.get_price(symbol)
            self.prices.append(price)

            # 2) Генеруємо сигнал
            signal = self.strategy.generate_signal(price)

            # 3) Симуляція / реальна торгівля
            if MODE == "SIMULATION":
                self.simulator.process_signal(signal, price)

            # 4) Лог
            self._log(f"Price: {price:.2f} | Signal: {signal}")

            time.sleep(1.0)

    # ------------- Оновлення UI -------------

    def _schedule_ui_update(self):
        self._update_ui()
        self.root.after(1000, self._schedule_ui_update)

    def _update_ui(self):
        # Статус
        status = "RUNNING" if self.running else "IDLE"
        if self.running and self.paused:
            status = "PAUSED"
        self.status_label.config(text=f"Status: {status}")

        # Графік
        if self.prices:
            self.ax_price.clear()
            self.ax_price.plot(self.prices, color="green")
            self.ax_price.set_title("Price")
            self.ax_price.set_xlabel("Tick")
            self.ax_price.set_ylabel("Price")
            self.canvas_price.draw_idle()

    # ------------- Допоміжне -------------

    def _log(self, msg: str):
        self.log_box.insert("end", f"{time.strftime('%H:%M:%S')} | {msg}\n")
        self.log_box.see("end")


if __name__ == "__main__":
    root = tk.Tk()
    app = TradingApp(root)
    root.mainloop()

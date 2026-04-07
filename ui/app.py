import tkinter as tk
from tkinter import simpledialog, filedialog
import time
import threading
import os

from core.recorder import Recorder
from core.player import Player
from core.loop_controller import LoopController
from core.screen_detector import ScreenDetector
from storage.macro_storage import MacroStorage
from storage.config_storage import ConfigStorage

from ui.components import (
    BG, BG_DARK, FG, FG_DIM,
    RED, ORANGE, GREEN, BLUE, TEAL, YELLOW, PURPLE,
    MenuBar, StatCard, FileLabel, StatusBar, LogBox, SettingsWindow,
    FONT_LABEL, FONT_SMALL
)


class App:

    def __init__(self):
        self.screen_detector = ScreenDetector(threshold=15, confirm_seconds=0)
        self.recorder        = Recorder(self.screen_detector)
        self.player          = Player(max_delay=1.0)
        self.loop_controller = LoopController(self.player, self.screen_detector)
        self.storage         = MacroStorage()
        self.config_storage  = ConfigStorage()

        self._current_file  = "nenhum"
        self._loop_start_time: float | None = None
        self._round_count   = 0
        self._timer_running = False

        self._build_window()

        saved = self.config_storage.load()

        # Variáveis de configuração
        self._cfg = {
            "delay_max":        tk.DoubleVar(value=saved["delay_max"]),
            "wait_before_f8":   tk.IntVar(value=saved["wait_before_f8"]),
            "wait_after_f8":    tk.IntVar(value=saved["wait_after_f8"]),
            "wait_after_enter": tk.IntVar(value=saved["wait_after_enter"]),
            "screen_threshold": tk.IntVar(value=saved["screen_threshold"]),
        }

        # Salva configurações
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self._build_menu()
        self._build_body()
        self._build_status_bar()
        self._connect_callbacks()


    def _build_window(self):
        self.root = tk.Tk()
        self.root.title("Macro — Elsword")
        self.root.geometry("780x400")
        self.root.configure(bg=BG)
        self.root.resizable(True, False)
        self.root.minsize(780, 400)

    

    def _build_menu(self):
        self.menu = MenuBar(self.root)

        # gravação
        self.btn_record   = self.menu.add_button("⏺  Gravar",      self._on_record_start, RED)
        self.btn_stop_rec = self.menu.add_button("⏹  Parar",        self._on_record_stop,  FG_DIM)
        self.menu.add_separator()

        # loop
        self.btn_start     = self.menu.add_button("▶  Iniciar Loop", self._on_loop_start,   GREEN)
        self.btn_stop_loop = self.menu.add_button("🛑  Parar Loop",  self._on_loop_stop,    ORANGE)
        self.menu.add_separator()

        # arquivo
        self.menu.add_button("💾  Salvar",   self._on_save, BLUE)
        self.menu.add_button("📂  Carregar", self._on_load, TEAL)
        self.menu.add_separator()

        # debug
        self.menu.add_button("🔍 Tela", self._on_debug_screen, PURPLE)

        # configurações
        self.menu.add_right_button("⚙️  Config", self._open_settings, YELLOW)

    def _on_debug_screen(self):
        brightness = self.screen_detector.get_screen_brightness()
        self.log_box.append(f"🔍 Brilho atual: {brightness:.1f}")

    def _build_body(self):
        # Nome do arquivo
        self.file_label = FileLabel(self.root)
        self.file_label.pack(fill="x", padx=20, pady=(12, 0))

        cards_frame = tk.Frame(self.root, bg=BG)
        cards_frame.pack(fill="x", padx=20, pady=14)

        self.card_rounds = StatCard(cards_frame, "Repetições",  GREEN)
        self.card_time   = StatCard(cards_frame, "Tempo rodando", BLUE)
        self.card_status = StatCard(cards_frame, "Status",       YELLOW)

        for card in [self.card_rounds, self.card_time, self.card_status]:
            card.pack(side="left", expand=True, fill="both", padx=6)

        self.card_status.set("Pronto")

        # separador
        tk.Frame(self.root, bg="#313244", height=1).pack(fill="x", padx=20, pady=(4, 0))

        # log
        tk.Label(self.root, text="LOG", font=("Segoe UI", 7),
                 bg=BG, fg=FG_DIM).pack(anchor="w", padx=22, pady=(6, 0))
        self.log_box = LogBox(self.root)
        self.log_box.pack(fill="both", expand=True, padx=20, pady=(2, 20))

    def _build_status_bar(self):
        self.status_bar = StatusBar(self.root)


    def _connect_callbacks(self):
        self.recorder.on_status_change  = lambda msg: self.root.after(0, lambda: self._set_status(msg))
        self.recorder.on_group_saved    = lambda groups: self.root.after(0, lambda: self.log_box.append(f"✅ Grupo {len(groups)} salvo ({len(groups[-1])} eventos)"))

        self.loop_controller.on_log           = lambda msg: self.root.after(0, lambda: self.log_box.append(msg))
        self.loop_controller.on_status_change = lambda msg: self.root.after(0, lambda: self._set_status(msg))
        self.loop_controller.on_round_complete = lambda n:  self.root.after(0, lambda: self._on_round_complete(n))


    def _on_record_start(self):
        self.screen_detector.threshold = self._cfg["screen_threshold"].get()
        self.recorder.start()
        self.log_box.append("🔴 Iniciando gravação...")

    def _on_record_stop(self):
        self.recorder.stop()
        self.log_box.append(f"⏹ Gravação parada — {len(self.recorder.groups)} grupos")

    def _on_loop_start(self):
        if not self.recorder.groups:
            self._set_status("⚠️ Carregue ou grave uma sequência primeiro!")
            return

        # Aplica configurações ao core
        self.player.max_delay                  = self._cfg["delay_max"].get()
        self.screen_detector.threshold         = self._cfg["screen_threshold"].get()
        self.loop_controller.wait_before_f8    = self._cfg["wait_before_f8"].get()
        self.loop_controller.wait_after_f8     = self._cfg["wait_after_f8"].get()
        self.loop_controller.wait_after_enter  = self._cfg["wait_after_enter"].get()

        self._round_count = 0
        self._loop_start_time = time.time()
        self.card_rounds.set("0")
        self._start_timer()
        self.loop_controller.start(self.recorder.groups)

    def _on_loop_stop(self):
        self.loop_controller.stop()
        self._stop_timer()

    def _on_save(self):
        if not self.recorder.groups:
            self.log_box.append("⚠️ Nada para salvar!")
            return
        name = simpledialog.askstring("Salvar", "Nome da gravação:", parent=self.root)
        if not name:
            return
        path = self.storage.save(self.recorder.groups, name)
        self._current_file = name
        self.file_label.set(name)
        self.log_box.append(f"💾 Salvo: {path}")

    def _on_load(self):
        path = filedialog.askopenfilename(
            initialdir=self.storage.default_dir,
            title="Carregar gravação",
            filetypes=[("JSON", "*.json")]
        )
        if not path:
            return
        self.recorder.groups = self.storage.load(path)
        name = os.path.splitext(os.path.basename(path))[0]
        self._current_file = name
        self.file_label.set(name)
        self.log_box.append(f"📂 Carregado: {name} ({len(self.recorder.groups)} grupos)")

    def _open_settings(self):
        SettingsWindow(self.root, self._cfg)


    def _on_round_complete(self, n: int):
        self._round_count = n
        self.card_rounds.set(str(n))

    def _start_timer(self):
        self._timer_running = True
        threading.Thread(target=self._timer_loop, daemon=True).start()

    def _stop_timer(self):
        self._timer_running = False

    def _timer_loop(self):
        while self._timer_running:
            elapsed = int(time.time() - self._loop_start_time)
            h = elapsed // 3600
            m = (elapsed % 3600) // 60
            s = elapsed % 60
            text = f"{h:02d}:{m:02d}:{s:02d}"
            self.root.after(0, lambda t=text: self.card_time.set(t))
            time.sleep(1)


    def _set_status(self, msg: str):
        self.status_bar.set(msg)

        # Atualiza o card de status com versão curta
        short = msg.replace("▶️", "").replace("⏳", "").replace("🔴", "").replace("✅", "").replace("🛑", "").replace("🎮", "").strip()
        if len(short) > 18:
            short = short[:16] + "…"
        self.card_status.set(short)


    def _on_close(self):
        self.config_storage.save({k: v.get() for k, v in self._cfg.items()})
        self.root.destroy()

    def run(self):
        self.root.mainloop()

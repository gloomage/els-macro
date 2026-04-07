import time
import threading
import pydirectinput
from core.player import Player
from core.screen_detector import ScreenDetector

pydirectinput.PAUSE = 0


class LoopController:
    """Orquestrar o loop infinito"""

    """
    Sequência de cada rodada:
      1. Executa cada grupo em ordem
      2. Aguarda loading entre grupos
      3. Ao final: espera N s → F8 → N s → Enter → N s → repete
    """

    def __init__(self, player: Player, screen_detector: ScreenDetector):
        self.player          = player
        self.screen_detector = screen_detector

        # Tempos configuráveis pela UI
        self.wait_before_f8   = 20
        self.wait_after_f8    = 3
        self.wait_after_enter = 10

        self._stop_flag = [False]

        # Callbacks para a UI
        self.on_log            = None
        self.on_status_change  = None
        self.on_round_complete = None

    def start(self, groups: list):
        if not groups:
            return
        self._stop_flag = [False]
        threading.Thread(target=self._loop, args=(groups,), daemon=True).start()

    def stop(self):
        self._stop_flag[0] = True
        self._log("🛑 Parando após a ação atual")

    def _loop(self, groups: list):
        self._status("▶️ Clique no jogo! 3s")
        self._log("▶️ Iniciando em 3 segundos")
        time.sleep(3)

        round_number = 1
        while not self._stop_flag[0]:
            self._log(f"─── Rodada {round_number} ───")

            if not self._play_all_groups(groups):
                break

            if self.on_round_complete:
                self.on_round_complete(round_number)

            self._log(f"✅ Rodada {round_number} concluída!")

            if not self._end_of_round_sequence():
                break

            round_number += 1

        self._status("🛑 Loop parado!")
        self._log("🛑 Loop parado!")

    def _play_all_groups(self, groups: list) -> bool:
        for i, group in enumerate(groups):
            if self._stop_flag[0]:
                return False

            self._status(f"▶️ Grupo {i + 1}/{len(groups)}")
            self._log(f"▶️ Executando Grupo {i + 1} ({len(group)} eventos)...")

            if not self.player.play_group(group, self._stop_flag):
                return False

            self._log(f"✅ Grupo {i + 1} concluído!")

            if i < len(groups) - 1:
                self._status("⏳ Aguardando loading...")
                self._log("⏳ Aguardando loading...")
                self.screen_detector.wait_for_loading(self._stop_flag)
                if self._stop_flag[0]:
                    return False
                time.sleep(1.5)
                self._log("🟢 Continuando próximo grupo...")

        return True

    def _end_of_round_sequence(self) -> bool:
        if not self._countdown(self.wait_before_f8, "⏳ Aguardando"):
            return False
        self._log("🎮 Apertando F8...")
        pydirectinput.press('f8')

        if not self._countdown(self.wait_after_f8, "⏳ F8 apertado"):
            return False
        self._log("🎮 Apertando Enter...")
        pydirectinput.press('return')

        if not self._countdown(self.wait_after_enter, "⏳ Reiniciando"):
            return False
        self._log("🟢 Reiniciado! Nova rodada...")
        return True

    def _countdown(self, seconds: int, label: str) -> bool:
        for i in range(seconds):
            if self._stop_flag[0]:
                return False
            self._status(f"{label}... {seconds - i}s")
            time.sleep(1)
        return True

    def _log(self, msg: str):
        if self.on_log:
            self.on_log(msg)

    def _status(self, msg: str):
        if self.on_status_change:
            self.on_status_change(msg)

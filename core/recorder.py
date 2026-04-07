import time
import threading
import keyboard
from core.screen_detector import ScreenDetector

TECLAS_MONITORAR = [
    'right', 'left', 'up', 'down',
    'z', 'x', 'c', 'v',
    'a', 's', 'd', 'f', 'g',
    'q', 'w', 'e', 'r', 't',
    '1', '2', '3', '4', '5', '6',
    'ctrl', 'space'
]


class Recorder:

    def __init__(self, screen_detector: ScreenDetector):
        self.screen_detector = screen_detector

        self.groups: list[list] = []       # grupos finalizados
        self._current_group: list = []     # grupo sendo gravado agora
        self._recording = False
        self._key_state: dict = {}         # estado anterior de cada tecla
        self._pressed_keys: set = set()    # teclas pressionadas agora (para UI)

        # Callbacks para notificar a UI
        self.on_group_saved = None         # chamado quando um grupo é salvo
        self.on_status_change = None       # chamado com mensagem de status
        self.on_keys_change = None         # chamado com set de teclas pressionadas

        threading.Thread(target=self._polling_loop, daemon=True).start()


    def start(self):
        self.groups.clear()
        self._current_group.clear()
        self._key_state.clear()
        self._recording = True
        self._notify_status(f"🔴 Gravando Grupo 1...")
        threading.Thread(target=self._loading_monitor, daemon=True).start()

    def stop(self):
        self._recording = False
        self._flush_current_group()
        self._notify_status(f"✅ {len(self.groups)} grupos gravados!")


    def _polling_loop(self):
        #Verifica o estado de cada tecla a cada 10ms e registra eventos de pressionar/soltar
        while True:
            if self._recording:
                for key in TECLAS_MONITORAR:
                    pressed = keyboard.is_pressed(key)
                    was_pressed = self._key_state.get(key, False)

                    if pressed and not was_pressed:
                        self._current_group.append(('down', key, time.time()))
                    elif not pressed and was_pressed:
                        self._current_group.append(('up', key, time.time()))

                    self._key_state[key] = pressed

            current = set(k for k in TECLAS_MONITORAR if keyboard.is_pressed(k))
            if current != self._pressed_keys:
                self._pressed_keys = current
                if self.on_keys_change:
                    self.on_keys_change(current)

            time.sleep(0.01)

    def _loading_monitor(self):

        black_since = None
        loading_active = False

        while self._recording:
            brightness = self.screen_detector.get_screen_brightness()
            is_black = brightness < self.screen_detector.threshold
            print(f"brilho: {brightness:.1f} | limiar: {self.screen_detector.threshold} | preto: {is_black}")

            if is_black:
                if black_since is None:
                    black_since = time.time()
                elif not loading_active and (time.time() - black_since) >= self.screen_detector.confirm_seconds:
                    loading_active = True
                    self._flush_current_group()
                    self._notify_status(f"⏳ Loading detectado! Grupo {len(self.groups)} salvo")
            else:
                if loading_active:
                    loading_active = False
                    black_since = None
                    time.sleep(1.5)
                    if self._recording:
                        num = len(self.groups) + 1
                        self._notify_status(f"🔴 Gravando Grupo {num}...")
                else:
                    black_since = None

            time.sleep(0.1)

    def _flush_current_group(self):
        #Salva o grupo atual se tiver eventos
        if self._current_group:
            self.groups.append(list(self._current_group))
            self._current_group.clear()
            self._key_state.clear()
            if self.on_group_saved:
                self.on_group_saved(self.groups)

    def _notify_status(self, msg: str):
        if self.on_status_change:
            self.on_status_change(msg)

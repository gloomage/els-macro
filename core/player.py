import time
import pydirectinput

pydirectinput.PAUSE = 0


class Player:

    def __init__(self, max_delay: float = 1.0):
        self.max_delay = max_delay

    def play_group(self, group: list, stop_flag: list) -> bool:
       
        for i, (action, key, timestamp) in enumerate(group):
            if stop_flag[0]:
                return False

            if i > 0:
                delay = group[i][2] - group[i - 1][2]
                time.sleep(min(delay, self.max_delay))

            try:
                if action == 'down':
                    pydirectinput.keyDown(key)
                elif action == 'up':
                    pydirectinput.keyUp(key)
            except Exception:
                pass

        return True

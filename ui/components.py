import tkinter as tk
from tkinter import scrolledtext

BG          = "#1e1e2e"
BG_DARK     = "#2e2e3e"
BG_MENU     = "#181825"
FG          = "#cdd6f4"
FG_DIM      = "#6c7086"
RED         = "#f38ba8"
ORANGE      = "#fab387"
GREEN       = "#a6e3a1"
BLUE        = "#89b4fa"
TEAL        = "#94e2d5"
YELLOW      = "#f9e2af"
PURPLE      = "#cba6f7"
DARK_RED    = "#e74c3c"
FONT_MONO   = ("Consolas", 9)
FONT_LABEL  = ("Segoe UI", 9)
FONT_VALUE  = ("Segoe UI", 22, "bold")
FONT_SMALL  = ("Segoe UI", 8)


class MenuBar(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent, bg=BG_MENU, height=32)
        self.pack(fill="x", side="top")
        self._items = []

    def add_button(self, label: str, command, color: str = FG) -> tk.Button:
        btn = tk.Button(
            self, text=label, command=command,
            bg=BG_MENU, fg=color,
            font=("Segoe UI", 9),
            relief="flat", bd=0,
            padx=10, pady=4,
            activebackground="#313244",
            activeforeground=color,
            cursor="hand2"
        )
        btn.pack(side="left")
        return btn

    def add_separator(self):
        tk.Frame(self, bg="#313244", width=1).pack(side="left", fill="y", pady=4)

    def add_right_button(self, label: str, command, color: str = FG) -> tk.Button:
        btn = tk.Button(
            self, text=label, command=command,
            bg=BG_MENU, fg=color,
            font=("Segoe UI", 9),
            relief="flat", bd=0,
            padx=10, pady=4,
            activebackground="#313244",
            activeforeground=color,
            cursor="hand2"
        )
        btn.pack(side="right")
        return btn


class StatCard(tk.Frame):
    """Card de número de repetição"""

    def __init__(self, parent, label: str, color: str = FG):
        super().__init__(parent, bg=BG_DARK, padx=20, pady=14)
        self._value_var = tk.StringVar(value="—")
        tk.Label(self, textvariable=self._value_var,
                 font=FONT_VALUE, bg=BG_DARK, fg=color).pack()
        tk.Label(self, text=label,
                 font=FONT_SMALL, bg=BG_DARK, fg=FG_DIM).pack()

    def set(self, value: str):
        self._value_var.set(value)


class FileLabel(tk.Frame):
    """Arquivo carregado"""

    def __init__(self, parent):
        super().__init__(parent, bg=BG, pady=6)
        tk.Label(self, text="ARQUIVO", font=("Segoe UI", 7),
                 bg=BG, fg=FG_DIM).pack()
        self._var = tk.StringVar(value="nenhum")
        tk.Label(self, textvariable=self._var,
                 font=("Segoe UI", 10), bg=BG, fg=BLUE).pack()

    def set(self, name: str):
        self._var.set(name)


class StatusBar(tk.Frame):
    """Status"""

    def __init__(self, parent):
        super().__init__(parent, bg=BG_MENU, height=22)
        self.pack(fill="x", side="bottom")
        self._var = tk.StringVar(value="Pronto")
        tk.Label(self, textvariable=self._var,
                 font=FONT_SMALL, bg=BG_MENU, fg=FG_DIM,
                 padx=8).pack(side="left")

    def set(self, msg: str, color: str = FG_DIM):
        self._var.set(msg)


class LogBox(scrolledtext.ScrolledText):
    """Log"""

    def __init__(self, parent, **kwargs):
        defaults = dict(bg=BG_DARK, fg=FG, font=FONT_MONO,
                        relief="flat", bd=0, state="disabled",
                        insertbackground=FG)
        defaults.update(kwargs)
        super().__init__(parent, **defaults)

    def append(self, msg: str):
        self.config(state="normal")
        self.insert(tk.END, msg + "\n")
        self.see(tk.END)
        self.config(state="disabled")


class SettingsWindow(tk.Toplevel):
    """Janela de configurações"""

    FIELDS = [
        ("delay_max",         "Delay máximo entre teclas (s)",       float, 1.0),
        ("wait_before_f8",    "Espera antes de apertar F8 (s)",       int,  20),
        ("wait_after_f8",     "Espera depois do F8 antes do Enter (s)", int, 3),
        ("wait_after_enter",  "Espera depois do Enter para começar (s)", int, 10),
        ("screen_threshold",  "Limiar tela preta (0-255)",             int,  20),
    ]

    def __init__(self, parent, vars_dict: dict):
        super().__init__(parent)
        self.title("Configurações")
        self.configure(bg=BG)
        self.resizable(False, False)
        self.grab_set()  # modal

        tk.Label(self, text="⚙️  Configurações", font=("Segoe UI", 12, "bold"),
                 bg=BG, fg=FG).pack(pady=(14, 8))

        frame = tk.Frame(self, bg=BG, padx=20)
        frame.pack(fill="x")

        for key, label, _, _ in self.FIELDS:
            row = tk.Frame(frame, bg=BG)
            row.pack(fill="x", pady=4)
            tk.Label(row, text=label, font=FONT_LABEL,
                     bg=BG, fg=FG, anchor="w", width=42).pack(side="left")
            tk.Entry(row, textvariable=vars_dict[key],
                     width=8, font=FONT_LABEL,
                     bg=BG_DARK, fg=FG,
                     insertbackground=FG,
                     relief="flat", justify="center").pack(side="right")

        tk.Label(frame,
                 text="Limiar tela preta: aumente se detectar loading falso.",
                 font=FONT_SMALL, bg=BG, fg=FG_DIM).pack(anchor="w", pady=(0, 4))

        tk.Button(self, text="Fechar", command=self.destroy,
                  bg=BG_DARK, fg=FG, font=FONT_LABEL,
                  relief="flat", padx=14, pady=6,
                  cursor="hand2").pack(pady=12)

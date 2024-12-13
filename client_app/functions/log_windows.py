import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from typing import Callable


class LogWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Error Logger")
        self.text_area = ScrolledText(
            self.root, wrap=tk.WORD, width=50, height=20)
        self.text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.text_area.configure(state=tk.DISABLED)

    def log_message(self, *messages: str, sep: str = ' ', end: str = '\n\n'):
        message = sep.join(map(str, messages)) + end
        self.root.after(0, self._append_message, message)

    def _append_message(self, message):
        self.text_area.configure(state=tk.NORMAL)
        self.text_area.insert(tk.END, message + "\n")
        self.text_area.configure(state=tk.DISABLED)
        self.text_area.see(tk.END)

    def run(self, on_close: Callable | None = None):
        if on_close is None:
            on_close = lambda: self.root.destroy()

        self.root.protocol("WM_DELETE_WINDOW", on_close)
        self.root.mainloop()

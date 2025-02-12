import tkinter as tk
from tkinter import ttk
from multiprocessing import Process
import sys
from tkinter import Canvas

sys.path.insert(1, 'functions')

from image_editing import uniq_tkinter
from converters import tkinter_converters
from big_post import tkinter_reddit_big_post
from parse_titles import tkinter_parse_titles
from acc_title_parse import tkinter_parse_acc_titles
from acc_subs_parse import tkinter_parse_acc_subs
from username_parse import tkinter_parse_username
from auto_post import tkinter_reddit_auto_post
from big_post_auto_titile import tkinter_reddit_big_post_auto_title
from auto_post_auto_titile import tkinter_reddit_auto_post_auto_title


import tkinter as tk
from tkinter import Canvas
from multiprocessing import Process

import tkinter as tk
from tkinter import Canvas
from multiprocessing import Process

class RoundedButton(Canvas):
    def __init__(self, parent, text, command=None, radius=25, btn_color="orange", text_color="white", **kwargs):
        width, height = 360, 60
        Canvas.__init__(self, parent, height=height, width=width, bg=parent["bg"], highlightthickness=0, **kwargs)
        self.command = command
        self.btn_color = btn_color
        self.text_color = text_color

        self.create_rounded_rect(2, 2, width - 2, height - 2, radius, fill=self.btn_color, outline=self.btn_color, width=0)
        self.text_id = self.create_text(width // 2, height // 2, text=text, fill=self.text_color, font=("Arial", 16, "bold"))  # Увеличен шрифт

        self.bind("<Button-1>", self.on_click)
        self.bind("<Enter>", self.on_hover)
        self.bind("<Leave>", self.on_leave)

    def create_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1, x2, y1 + radius,
            x2, y2 - radius,
            x2, y2, x2 - radius, y2,
            x1 + radius, y2,
            x1, y2, x1, y2 - radius,
            x1, y1 + radius,
            x1, y1
        ]
        self.create_polygon(points, smooth=True, **kwargs)

    def on_click(self, event):
        if self.command:
            Process(target=self.command, daemon=True).start()

    def on_hover(self, event):
        self.itemconfig(self.text_id, fill="black")

    def on_leave(self, event):
        self.itemconfig(self.text_id, fill=self.text_color)

def create_window():
    root = tk.Tk()
    root.title("Master Karma")
    root.geometry("420x650")
    root.configure(bg="#f0f0f0")
    root.resizable(False, False)

    main_frame = tk.Frame(root, bg="#f0f0f0")
    main_frame.pack(fill="both", expand=True)

    canvas = tk.Canvas(main_frame, bg="#f0f0f0", highlightthickness=0)
    scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg="#f0f0f0")

    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=400)  # Оптимизировано под ширину кнопок
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    label = tk.Label(scrollable_frame, text="Choose a Function", font=("Arial", 18, "bold"), bg="#f0f0f0")
    label.pack(pady=5)

    buttons = [
        ("Parse Titles From User Account", tkinter_parse_acc_titles),
        ("Parse Subs From User Account", tkinter_parse_acc_subs),
        ("Parse Titles From Subreddit", tkinter_parse_titles),
        ("Parse Usernames From Subreddit", tkinter_parse_username),
        ("Post Preparation with parsed titles", tkinter_reddit_big_post_auto_title),
        ("Post Preparation with your titles", tkinter_reddit_big_post),
        ("Full post with your titles", tkinter_reddit_auto_post),
        ("Full post with parsed titles", tkinter_reddit_auto_post_auto_title),
        ("Unify photo or video", uniq_tkinter),
        ("Converters", tkinter_converters)
    ]

    for text, func in buttons:
        button = RoundedButton(scrollable_frame, text=text, command=func)
        button.pack(pady=6)

    root.mainloop()

if __name__ == "__main__":
    create_window()

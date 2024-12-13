import tkinter as tk
from multiprocessing import Process
import sys

sys.path.insert(1, 'functions')

from image_editing import uniq_tkinter
from converters import tkinter_converters
from big_post import tkinter_reddit_big_post
from parse_titles import tkinter_parse_titles
from acc_title_parse import tkinter_parse_acc_titles
from acc_subs_parse import tkinter_parse_acc_subs
from username_parse import tkinter_parse_username
from auto_post import tkinter_reddit_auto_post


def create_window():
    root = tk.Tk()
    root.title("Reddit Soft")

    root.geometry("400x400")

    root.configure(bg="#f0f0f0")

    main_frame = tk.Frame(root)
    main_frame.pack(fill="both", expand=True)

    canvas = tk.Canvas(main_frame, bg="#f0f0f0")
    scrollbar = tk.Scrollbar(
        main_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg="#f0f0f0")

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    button_config = {
        "font": ("Modern No. 20", 14, "bold"),
        "bg": "black",
        "fg": "white",
        "activebackground": "#45a049",
        "activeforeground": "black",
        "bd": 3,
        "relief": "raised",
        "width": 28,
        "height": 2
    }

    label = tk.Label(scrollable_frame, text="Choose a Function",
                     font=("Modern No. 20", 18), bg="#f0f0f0")
    label.pack(pady=10)

    buttons = [
        ("Parse Titles From User Account", tkinter_parse_acc_titles),
        ("Parse Subs From User Account", tkinter_parse_acc_subs),
        ("Parse Titles From Subreddit", tkinter_parse_titles),
        ("Parse Usernames From Subreddit", tkinter_parse_username),
        ("Prepareation for post", tkinter_reddit_big_post),
        ("Full post", tkinter_reddit_auto_post),
        ("Uniqueize photo or video", uniq_tkinter),
        ("Converters", tkinter_converters),
    ]

    def start_process(func):
        Process(target=func, daemon=True).start()

    for text, func in buttons:
        button = tk.Button(
            scrollable_frame,
            text=text,
            command=lambda f=func: start_process(f),
            **button_config
        )

        button.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    create_window()

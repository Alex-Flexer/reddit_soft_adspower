from PIL import Image
from moviepy import VideoFileClip
import os
import tkinter as tk
from tkinter import filedialog
from log_windows import LogWindow


def convert_to_png(input_path, output_folder='output'):
    log_window = LogWindow()
    try:
        filename = os.path.splitext(os.path.basename(input_path))[0]
        output_path = os.path.join(output_folder, f"{filename}.png")

        with Image.open(input_path) as img:
            img.save(output_path, 'PNG')
            log_window.log_message(f"Converted '{input_path}' to '{output_path}' successfully.")
    except Exception as e:
        log_window.log_message(f"Error converting '{input_path}' to PNG: {e}")


def convert_to_mp4(input_path, output_folder='output'):
    log_window = LogWindow()
    try:
        filename = os.path.splitext(os.path.basename(input_path))[0]
        output_path = os.path.join(output_folder, f"{filename}.mp4")

        with VideoFileClip(input_path) as video:
            video.write_videofile(output_path, codec='libx264')
            log_window.log_message(f"Converted '{input_path}' to '{output_path}' successfully.")
    except Exception as e:
        log_window.log_message(f"Error converting '{input_path}' to MP4: {e}")


def tkinter_converters():
    def browse_file():
        file_path = filedialog.askopenfilename()
        entry_path.delete(0, tk.END)
        entry_path.insert(0, file_path)

    def convert():
        input_path = entry_path.get()
        output_folder = 'output'

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        if conversion_choice.get() == 'png':
            convert_to_png(input_path, output_folder)
        elif conversion_choice.get() == 'mp4':
            convert_to_mp4(input_path, output_folder)

    root = tk.Tk()
    root.title("File Converter")

    tk.Label(root, text="Select a file:").grid(row=0, column=0, padx=10, pady=10)
    entry_path = tk.Entry(root, width=50)
    entry_path.grid(row=0, column=1, padx=10, pady=10)
    tk.Button(root, text="Browse", command=browse_file).grid(row=0, column=2, padx=10, pady=10)

    conversion_choice = tk.StringVar(value='png')
    tk.Radiobutton(root, text="Convert to PNG", variable=conversion_choice, value='png').grid(row=1, column=0, padx=10, pady=10)
    tk.Radiobutton(root, text="Convert to MP4", variable=conversion_choice, value='mp4').grid(row=1, column=1, padx=10, pady=10)

    tk.Button(root, text="Convert", command=convert).grid(row=2, column=1, padx=10, pady=10)

    root.mainloop()
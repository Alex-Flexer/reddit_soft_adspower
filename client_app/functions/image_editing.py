import tkinter as tk
from tkinter import filedialog, messagebox
import os
from PIL import Image
from moviepy import VideoFileClip
from threading import Thread

from log_windows import LogWindow
from db_funcs import get_reddit_accounts
from tkinter import messagebox

user_email = None

from keyring import get_password

def uniq_tkinter():

    global user_email
    user_email = get_password("user", "email")

    if user_email is None:
        messagebox.showerror('No accounts bought')
    accounts, msg = get_reddit_accounts(user_email)

    def uniqueize(logger: LogWindow, tp: str, input_path, amount):
        def get_file_extension(file_path: str) -> str:
            _, extension = os.path.splitext(file_path)
            return extension

        def process_image(input_path, output_path, degree, sides: dict[str, int]) -> None | Exception:
            try:
                with Image.open(input_path) as img:
                    width, height = img.size
                    cropped_img = img.crop(
                        (sides["l"], sides["u"], width -
                         sides["r"], height - sides["d"])
                    )

                    rotated_img = cropped_img.rotate(degree, expand=True)
                    rotated_img.save(output_path)
            except Exception as e:
                return e

        def process_video(input_path, output_path, degree, sides: dict[str, int]) -> None | Exception:
            try:
                clip = VideoFileClip(input_path)
                width, height = clip.size

                cropped_clip = clip.cropped(
                    x1=sides["l"],
                    y1=sides["d"],
                    x2=width-sides["r"],
                    y2=height-sides["u"]
                )

                rotated_clip = cropped_clip.rotated(degree)

                rotated_clip.write_videofile(
                    output_path, codec="libx264", audio_codec="aac")
                clip.close()
            except Exception as e:
                return e

        cnt = 1
        flag = True
        output_path = os.path.join(os.path.dirname(input_path), "copies")
        cnt_to_change_out_path = 0
        orig_output_path = output_path
        while os.path.exists(output_path):
            output_path = f"{orig_output_path}({cnt_to_change_out_path})"
            cnt_to_change_out_path += 1

        os.mkdir(output_path)
        for deg in range(3, 8):
            for l in range(1, 11):
                for u in range(1, 11):
                    for r in range(1, 11):
                        for d in range(1, 11):
                            sides = {"l": l, "r": r, "u": u, "d": d}
                            args = (
                                input_path,
                                os.path.join(output_path, str(
                                    cnt) + get_file_extension(input_path)),
                                deg / 10,
                                sides
                            )
                            print(args)
                            res =\
                                process_image(*args)\
                                if tp == "img"\
                                else process_video(*args) if tp == "video"\
                                else Exception("Unknown type of file")

                            if res is None:
                                logger.log_message(
                                    f"{cnt}th file is loaded successfully")
                            else:
                                logger.log_message(f"{cnt}th file was failed")

                            cnt += 1
                            if cnt > amount or res is not None:
                                if isinstance(res, Exception):
                                    logger.log_message(str(res))
                                else:
                                    logger.log_message(
                                        "File have been successfully uniqueized")
                                flag = False
                                break
                        if not flag:
                            break
                    if not flag:
                        break
                if not flag:
                    break
            if not flag:
                break

    def select_file():
        file_path = filedialog.askopenfilename()
        if file_path and\
                os.path.exists(file_path) and\
                os.path.isfile(file_path):

            entry_file.delete(0, tk.END)
            entry_file.insert(0, file_path)
        else:
            messagebox.showerror("Error", "Invalid file path!")

    def start_uniqueization():
        selected_function = function_var.get()
        file_path = entry_file.get()
        amount = int(entry_amount.get())

        if not file_path:
            messagebox.showerror("Error", "Please select a file")
            return

        valid_video_extensions = {".mp4", ".avi", ".mov"}
        valid_photo_extensions = {".jpg", ".jpeg", ".png"}

        file_extension = file_path.split(".")[-1].lower()
        tp = None
        if selected_function == "Video":
            if f".{file_extension}" not in valid_video_extensions:
                messagebox.showerror(
                    "Error", "Please select a valid video file")
                return
            tp = "video"
        elif selected_function == "Photo":
            if f".{file_extension}" not in valid_photo_extensions:
                messagebox.showerror(
                    "Error", "Please select a valid photo file")
                return
            tp = "img"
        else:
            messagebox.showerror("Error", "Please select a function")
            return

        root.destroy()
        logger = LogWindow()
        uniq_thread =\
            Thread(
                target=uniqueize,
                args=(
                    logger,
                    tp,
                    file_path,
                    amount
                ),
                daemon=True
            )
        uniq_thread.start()
        logger.run()

    root = tk.Tk()
    root.title("Uniqueizer")
    root.resizable(False, False)

    tk.Label(root, text="Select file:", font=("Modern No. 20", 18)).grid(
        row=0, column=0, padx=10, pady=10)
    entry_file = tk.Entry(root, width=50)
    entry_file.grid(row=0, column=1, padx=10, pady=10)

    valid = root.register(lambda text: text.isdigit())
    tk.Label(root, text="Enter amount of copies:", font=("Modern No. 20", 18)).grid(
        row=1, column=0, padx=10, pady=10)

    entry_amount = tk.Entry(root, width=20, validate="key",
                            validatecommand=(valid, "%S"))
    entry_amount.grid(row=1, column=1, padx=10, pady=10)

    tk.Button(root, text="Browse", font=("Modern No. 20", 18),
              command=select_file).grid(row=0, column=2, padx=10, pady=10)

    function_var = tk.StringVar(value="Photo")
    tk.Radiobutton(
        root,
        text="Uniqueize Video",
        font=("Modern No. 20", 18),
        variable=function_var, value="Video").\
        grid(row=2, column=0, padx=10, pady=5)

    tk.Radiobutton(
        root,
        text="Uniqueize Photo",
        font=("Modern No. 20", 18),
        variable=function_var,
        value="Photo").\
        grid(row=2, column=1, padx=10, pady=5)

    tk.Button(root,
              text="Start",
              font=("Modern No. 20", 18),
              command=start_uniqueization).\
        grid(row=3, column=0, columnspan=3, pady=10)

    status_label = tk.Label(root, text="Ready", font=("Modern No. 20", 18))
    status_label.grid(row=4, column=0, columnspan=3, pady=10)

    root.mainloop()

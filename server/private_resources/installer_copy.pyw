from os import system, mkdir, remove
from sys import executable

system(f"{executable} -m pip install requests")
system(f"{executable} -m pip install tk")

from requests import post, ConnectionError
from tkinter import Tk, Label, Entry, Button, filedialog, messagebox

from json import dumps
from os.path import join, exists
from zipfile import ZipFile


def download_software(
        username: str,
        password: str,
        folder_path: str
) -> tuple[int, str | None]:

    data = dumps({"email": username, "password": password})
    try:
        resp = post("http://reddsyndicate.com/get/software", data=data)
    except ConnectionError:
        return -1, None

    if resp.status_code != 200 or not exists(folder_path):
        return resp.status_code, None

    download_path = join(folder_path, "software.zip")
    with open(download_path, "wb") as f:
        f.write(resp.content)
    return 200, download_path


def remove_archive(path_to_archive: str) -> None:
    remove(path_to_archive)


def download_requirements(path_to_requirements: str):
    system(f"{executable} -m pip install -r \"{path_to_requirements}\"")


def login_user(username: str, password: str) -> tuple[bool, str]:
    data = dumps({"email": username, "password": password})
    try:
        resp = post("http://reddsyndicate.com/login/user", data=data)
    except ConnectionError:
        return False, "Network error"
    else:
        json = resp.json()
        return json["result"], json["message"]


def extract_zip(zip_path: str, extract_to: str):
    with ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)


def login_window():
    def validate_login():
        username = username_entry.get()
        password = password_entry.get()

        if not username or not password:
            messagebox.showerror(
                "Error", "Please enter username and password!")
            return

        is_logged, message = login_user(username, password)
        if is_logged:
            messagebox.showinfo("Success", "Login successful!")
            root.destroy()
            file_selection_window(username, password)
        else:
            messagebox.showerror("Error", message)

    root = Tk()
    root.title("Login")
    root.geometry("300x200")

    Label(root, text="Telegram Username:").pack(pady=5)
    username_entry = Entry(root, width=30)
    username_entry.pack(pady=5)

    Label(root, text="Password:").pack(pady=5)
    password_entry = Entry(root, width=30, show="*")
    password_entry.pack(pady=5)

    submit_button = Button(root, text="Login", command=validate_login)
    submit_button.pack(pady=10)

    root.mainloop()


def file_selection_window(username: str, password: str):
    def download_and_extract():
        folder_path = filedialog.askdirectory(
            title="Select folder for download")
        if not folder_path:
            messagebox.showerror("Error", "No folder selected!")
            return

        messagebox.showinfo(
            "Information", "Downloading started. Please wait...")
        code, zip_path = download_software(username, password, folder_path)

        if code != 200:
            error_text = ""
            match code:
                case 400:
                    error_text = "Incorrect request"
                case 404:
                    error_text = "User with this email does not exist"
                case 403:
                    error_text = "Incorrect credentials"
                case "_":
                    error_text = "Unknown error"

            messagebox.showerror("Error", error_text)
            return

        try:
            folder_path = join(folder_path, "RedditSyndicate")
            mkdir(folder_path)
            extract_zip(zip_path, folder_path)
            messagebox.showinfo(
                "Success", f"Archive successfully extracted to {folder_path}")

        except Exception as e:
            messagebox.showerror(
                "Error", f"Failed to extract archive: {str(e)}")
        else:
            remove_archive(zip_path)
            download_requirements(join(folder_path, "requirements.txt"))
            messagebox.showinfo("Success", "Requirements was successfully installed")
        finally:
            root.destroy()

    root = Tk()
    root.title("Folder Selection")
    root.geometry("300x150")

    label_text = "Select folder for downloading and extracting the file"
    Label(root, text=label_text).pack(pady=10)

    download_button = Button(
        root,
        text="Select Folder",
        command=download_and_extract
    )
    download_button.pack(pady=10)

    root.mainloop()


if __name__ == "__main__":
    login_window()

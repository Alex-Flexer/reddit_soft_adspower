from os import system
from os.path import split as split_path
from shutil import move, rmtree, make_archive


def obfuscate_client_app(original_path: str, final_path: str) -> None:
    system(f"pyarmor gen -O dist {original_path} --platform windows.x86_64")
    main_folder_name = split_path(original_path)[1]
    move("./dist/pyarmor_runtime_000000", f"./dist/{main_folder_name}")
    move(f"./dist/{main_folder_name}", final_path)
    rmtree("./dist")


def zip_directory(directory: str, output_file: str):
    make_archive(output_file, 'zip', directory)


def main():
    path_to_obfuscated_client_app = './private_resources/client_app'
    path_to_client_app = '../client_app'
    path_to_zipped_client_app = './private_resources/source'

    obfuscate_client_app(path_to_client_app, path_to_obfuscated_client_app)
    zip_directory(path_to_obfuscated_client_app, path_to_zipped_client_app)
    rmtree(path_to_obfuscated_client_app)


if __name__ == '__main__':
    main()

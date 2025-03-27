import os
import shutil


def copy_file(source, dest, bytes_mode=False):
    read_mode = "rb" if bytes_mode else "r"
    write_mode = "wb" if bytes_mode else "w"
    with open(source, read_mode) as s:
        with open(dest, write_mode) as d:
            shutil.copyfileobj(s, d)


def copy_folder_content(source, dest):
    if not os.path.exists(dest):
        os.mkdir(dest)
    for entry in os.listdir(source):
        with open(os.path.join(source, entry), "rb") as s:
            with open(os.path.join(dest, entry), "wb") as d:
                shutil.copyfileobj(s, d)

import os
from zipfile import ZipFile
from pathlib import Path


VALID_IMAGE_TYPES = [".jpg", ".gif", ".png", ".webp", ".jpeg", ".gif", ".tiff", ".bmp", ".svg"]


def archive_images(images_folder_path: str) -> str:
    images = [os.path.join(images_folder_path, file_name) for file_name in os.listdir(images_folder_path)
              if is_valid_file(file_name)]
    archive_name = get_archive_name(images_folder_path)
    full_archive_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), archive_name)
    with ZipFile(full_archive_file_path, "w") as archive:
        for image in images:
            rel_path = os.path.relpath(image, start=images_folder_path)
            archive.write(image, arcname=rel_path)

    return full_archive_file_path


def write_archive_from_bytes(archive_file_path: str, content_in_bytes: bytes):
    with open(archive_file_path, "wb") as local_file:
        local_file.write(content_in_bytes)


def get_archive_name(folder_path: str):
    return f"{Path(folder_path).stem}.zip"


def is_valid_file(file_name: str) -> bool:
    return Path(file_name).suffix in VALID_IMAGE_TYPES

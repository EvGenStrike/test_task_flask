import os
import requests
import time
import archive_manager


SERVER_URL = "http://127.0.0.1:5000/"
DOWNLOAD_TO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "processed_images")
PING_FREQUENCY = 1


def upload_images(images_folder_path: str) -> dict:
    archive_path = archive_manager.archive_images(images_folder_path)
    with open(archive_path, "rb") as archive:
        files = {"archived_images": archive}
        try:
            response = requests.post(f"{SERVER_URL}/upload_archive", files=files)
        except (ConnectionRefusedError, requests.exceptions.ConnectionError) as error:
            return {"success": False, "message": "Ошибка доступа сервера. Попробуйте позже"}

    os.remove(archive_path)
    return response.json()


def download_processed_archive() -> None:
    response = requests.get(f"{SERVER_URL}/download_processed_archive")

    if not os.path.exists(DOWNLOAD_TO_PATH):
        os.makedirs(DOWNLOAD_TO_PATH)
    if response.status_code == 200:
        content_disposition = response.headers.get("Content-Disposition")
        filename = f"{str(int(time.time()))}.zip"
        if content_disposition and "filename=" in content_disposition:
            filename = content_disposition.split("filename=")[1].strip('"')
        else:
            print(f"Ошибка получения имени файла. Файл будет сохранён под именем {filename}")
        local_file_path = os.path.join(DOWNLOAD_TO_PATH, filename)
        archive_manager.write_archive_from_bytes(local_file_path, response.content)
        full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), local_file_path)
        print(f"Архив успешно сохранён по пути: {full_path}")
    else:
        print(f"Ошибка при скачивании архива: {response.status_code} - {response.text}")


def check_document_status(server_url: str) -> dict:
    response = requests.get(f"{server_url}/check_status")
    return response.json()


def input_image_folder_path() -> str:
    while not os.path.isdir(image_folder_path := input("Введите путь к папке с изображениями: ")):
        print("Данный путь неверный или не существует. ")
    return image_folder_path


def ping_server_is_processing_done() -> bool:
    while True:
        print("Проверка готовности обработки изображений...")
        status = check_document_status(SERVER_URL)
        if not status["is_processing_done"]:
            print(f"Изображения ещё обрабатываются. Повторная проверка через {PING_FREQUENCY} сек...")
            time.sleep(PING_FREQUENCY)
        else:
            print("Изображения успешно обработаны. Скачивание результата...")
            return True


def run() -> None:
    image_folder_path = input_image_folder_path()
    result = upload_images(image_folder_path)
    print(result["message"])
    if not result["success"]:
        return
    if ping_server_is_processing_done():
        download_processed_archive()

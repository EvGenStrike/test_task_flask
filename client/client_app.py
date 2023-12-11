import os
import requests
import time
import archivizer


class ClientApp:
    __server_url = "http://127.0.0.1:5000/"
    __download_to_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "processed_images")

    def __init__(self,
                 server_url: str = None,
                 download_to_path: str = None,
                 ping_frequency: int = 1):
        self.__server_url = self.__server_url if server_url is None else server_url
        self.__download_to_path = self.__download_to_path if download_to_path is None else download_to_path
        self.__ping_frequency = ping_frequency

    def run(self) -> None:
        image_folder_path = self.__input_image_folder_path()
        result = self.__upload_images(image_folder_path)
        print(result["message"])
        if not result["success"]:
            return
        if self.__ping_server_is_processing_done():
            print("Изображения успешно обработаны. Скачивание результата...")
            self.__download_processed_archive()

    def __upload_images(self, images_folder_path: str) -> dict:
        archive_path = archivizer.archive_images(images_folder_path)
        with open(archive_path, "rb") as archive:
            files = {"archived_images": archive}
            try:
                response = requests.post(f"{self.__server_url}/upload_archive", files=files)
                answer = response.json()
            except (ConnectionRefusedError, requests.exceptions.ConnectionError) as error:
                answer = {"success": False, "message": f"Ошибка доступа сервера {error}. Попробуйте позже"}

        os.remove(archive_path)
        return answer

    def __download_processed_archive(self) -> None:
        response = requests.get(f"{self.__server_url}/download_processed_archive")

        if not os.path.exists(self.__download_to_path):
            os.makedirs(self.__download_to_path)
        if response.status_code == 200:
            content_disposition = response.headers.get("Content-Disposition")
            filename = f"{str(int(time.time_ns()))}.zip"
            if content_disposition and "filename=" in content_disposition:
                filename = content_disposition.split("filename=")[1].strip('"')
            else:
                print(f"Ошибка получения имени файла. Файл будет сохранён под именем {filename}")
            local_file_path = os.path.join(self.__download_to_path, filename)
            archivizer.write_archive_from_bytes(local_file_path, response.content)
            full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), local_file_path)
            print(f"Архив успешно сохранён по пути: {full_path}")
        else:
            print(f"Ошибка при скачивании архива: {response.status_code} - {response.text}")

    def __check_document_status(self) -> dict:
        response = requests.get(f"{self.__server_url}/check_status")
        return response.json()

    def __input_image_folder_path(self) -> str:
        while not os.path.isdir(image_folder_path := input("Введите путь к папке с изображениями: ")):
            print("Данный путь неверный или не существует. ")
        return image_folder_path

    def __ping_server_is_processing_done(self) -> bool:
        while True:
            print("Проверка готовности обработки изображений...")
            status = self.__check_document_status()
            if not status["is_processing_done"]:
                print(f"Изображения ещё обрабатываются. Повторная проверка через {self.__ping_frequency} сек...")
                time.sleep(self.__ping_frequency)
            return True

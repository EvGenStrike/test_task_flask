import os
import shutil
import time
import random
import patoolib
from pathlib import Path
from werkzeug.datastructures import FileStorage


class Processing:
    MAX_PREVIOUS_DIRS_COUNT = 5
    MAX_PREVIOUS_ZIPS_COUNT = 5
    __UPLOAD_DIRECTORY = "uploaded_images"

    __is_processing_done = False
    __extract_to_path = None
    __archive_file = None
    __upload_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), __UPLOAD_DIRECTORY)

    def __init__(self, archive_file: FileStorage, upload_directory: str = None):
        self.__is_processing_done = False
        self.__archive_file = archive_file
        self.__upload_directory = self.__upload_directory if upload_directory is None else upload_directory

    @property
    def is_processing_done(self):
        return self.__is_processing_done

    @property
    def extracted_images_path(self):
        return self.__extract_to_path

    def extract_archive(self) -> None:
        if not os.path.exists(self.__upload_directory):
            os.makedirs(self.__upload_directory)

        self.__extract_to_path = os.path.join(self.__upload_directory, str(int(time.time_ns())))
        os.makedirs(self.__extract_to_path)
        self.__delete_excess_dirs(self.__upload_directory)

        temp_archive_file_path = os.path.join(self.__extract_to_path, self.__archive_file.filename)
        self.__archive_file.save(temp_archive_file_path)
        self.__archive_file.close()

        patoolib.extract_archive(temp_archive_file_path, outdir=self.__extract_to_path)
        os.remove(temp_archive_file_path)

    def process_images_in_archive(self) -> None:
        # имитация обработки изображений
        min_sleep_time = 2
        max_sleep_time = 5
        sleep_time = random.uniform(min_sleep_time, max_sleep_time)
        time.sleep(sleep_time)
        self.__is_processing_done = True

    def archive_processed_images(self) -> str:
        shutil.make_archive(self.__extract_to_path, "zip", self.__extract_to_path)
        self.__delete_excess_zips(self.__upload_directory)
        return f"{self.__extract_to_path}.zip"

    def __delete_excess_dirs(self, current_directory: str):
        directories = [directory for directory in os.listdir(current_directory)
                       if os.path.isdir(os.path.join(current_directory, directory))]
        while len(directories) > self.MAX_PREVIOUS_DIRS_COUNT:
            shutil.rmtree(os.path.join(current_directory, directories[0]))
            directories.pop(0)

    def __delete_excess_zips(self, current_directory: str):
        zips = [zip_file for zip_file in os.listdir(current_directory) if Path(zip_file).suffix == ".zip"]
        while len(zips) > self.MAX_PREVIOUS_ZIPS_COUNT:
            os.remove(os.path.join(self.__upload_directory, zips[0]))
            zips.pop(0)

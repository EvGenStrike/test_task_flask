import os.path
from flask import Flask, request, jsonify, send_file
from processing import Processing
from threading import Thread


app = Flask(__name__)

processor: Processing


@app.route("/upload_archive", methods=["POST"])
def upload_archive():
    try:
        global processor
        processor = Processing(request.files["archived_images"])
        processor.extract_archive()
        Thread(target=background_processing).start()
        return jsonify({"success": True,
                        "message": "Архив успешно загружен и распакован!\n"
                                   "Идёт обработка изображений..."})
    except Exception as error:
        print(f"Ошибка при обработке запроса: {str(error)}")

        return jsonify({"success": False,
                        "message": "Ошибка при обработке запроса"}), 500


@app.route("/check_status", methods=["GET"])
def check_status():
    global processor
    return jsonify({"is_processing_done": None if processor is None else processor.is_processing_done})


@app.route("/download_processed_archive", methods=["GET"])
def download_processed_archive():
    global processor
    if processor.is_processing_done:
        try:
            archive_path = processor.archive_processed_images()
            return send_file(archive_path, as_attachment=True, download_name=os.path.basename(archive_path))
        except Exception as error:
            print(f"Ошибка при скачивании архива: {str(error)}")
            return jsonify({"error": "Ошибка при скачивании архива"}), 500
    else:
        return jsonify({"error": "Архив еще не обработан"}), 404


def background_processing() -> None:
    global processor
    processor.process_images_in_archive()


if __name__ == "__main__":
    app.run()

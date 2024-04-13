import flask
import noted
from pathlib import Path
from uuid import uuid4
import noted.api
import noted.api.audio
import re


@noted.app.route("/api/v1/upload/", methods=["POST"])
def upload_file():
    if "file" not in flask.request.files:
        return "No file part", 404
    file = flask.request.files["file"]
    if file.filename == "":
        return "No selected file", 404
    filename = re.sub(r"[^a-zA-Z0-9]+", "", file.filename)
    # create unique filename
    unique_id = uuid4()
    filename = Path(f"{unique_id}{filename}")
    filepath = noted.app.config["VIDEO_FOLDER"] / filename
    file.save(filepath)
    audio_file = noted.api.audio.extract_audio(
        filepath, noted.app.config["AUDIO_FOLDER"]
    )
    return flask.jsonify(
        {"video": f"/download/{filename}", "audio": f"/download/{audio_file}"}
    )


@noted.app.route("/api/v1/download/<filename>", methods=["GET"])
def download_file(filename):
    filename = Path(filename)
    suffix = Path(filename).suffix
    if suffix == ".mp3":
        folder = noted.app.config["AUDIO_FOLDER"]
    else:
        folder = noted.app.config["VIDEO_FOLDER"]
    filepath = folder / filename
    return flask.send_from_directory(filepath, as_attachment=True)


@noted.app.route("/api/v1/predict/", methods=["GET"])
def predict():
    pass

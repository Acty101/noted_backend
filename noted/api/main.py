import flask
import noted
from pathlib import Path
from uuid import uuid4
import noted.api.audio
import re
import noted.model
import logging
from google.api_core.exceptions import RetryError, ResourceExhausted

LOGGER = logging.getLogger(__name__)


@noted.app.route("/", methods=["GET"])
def get_routes():
    return flask.jsonify(
        {
            "routes": [
                "/api/v1/download/<filename>",
                "/api/v1/upload/",
                "/api/v1/predict/<filename>",
            ]
        }
    )


@noted.app.route("/api/v1/upload/", methods=["POST"])
def upload_file():
    if "file" not in flask.request.files:
        return flask.jsonify(make_err_response("No file part")), 404
    file = flask.request.files["file"]
    if file.filename == "":
        return flask.josnify(make_err_response("No selected file")), 404
    filename = re.sub(r"[^a-zA-Z0-9.]+", "", file.filename)
    # create unique filename
    unique_id = uuid4()
    filename = Path(f"{unique_id}{filename}")

    # if audio only, we dont need to strip
    if filename.suffix == ".mp3":
        file.save(noted.app.config["AUDIO_FOLDER"] / filename)
        return flask.jsonify(
            {
                "video": "",
                "audio": f"{filename}",
            }
        )

    filepath = noted.app.config["VIDEO_FOLDER"] / filename
    file.save(filepath)
    audio_file = noted.api.audio.extract_audio(
        filepath, noted.app.config["AUDIO_FOLDER"]
    )
    return flask.jsonify(
        {
            "video": f"{filename}",
            "audio": f"{audio_file}",
        }
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
    return flask.send_from_directory(filepath, as_attachment=True), 200


@noted.app.route("/api/v1/predict/<filename>", methods=["GET"])
def predict(filename):
    filename = Path(filename)
    suffix = filename.suffix
    LOGGER.info("Request received..")
    if suffix == ".mp3":
        LOGGER.info("Starting prediction...")
        try:
            model_response = noted.model.predict_audio(
                noted.app.config["AUDIO_FOLDER"] / filename,
                noted.app.config["AUDIO_PROMPT"],
                noted.app.config["MODEL"],
            )
        except (RetryError, ResourceExhausted) as e:
            return flask.jsonify(make_err_response("Error with Gemini")), 408
        LOGGER.info("Prediction done!")
        return flask.jsonify({"response": model_response})
    return flask.jsonify({"hello": "world"})
    # else:
    #     predict_video(noted.app.config["VIDEO_FOLDER"] / filename)


def make_err_response(err):
    return {"error": err}

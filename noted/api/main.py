import flask
import noted
from pathlib import Path
from uuid import uuid4
import noted.api.audio
import re
import noted.model
import logging
from google.api_core.exceptions import RetryError, ResourceExhausted
from enum import Enum
import requests

LOGGER = logging.getLogger(__name__)


@noted.app.route("/", methods=["GET"])
def get_routes():
    return flask.redirect("/api/v1/")


@noted.app.route("/api/v1/", methods=["GET"])
def get_api_routes():
    return flask.jsonify(
        {
            "routes": [
                "/api/v1/download/<filename>",
                "/api/v1/upload/",
                "/api/v1/predict/<filename>",
            ]
        }
    )


@noted.app.route("/api/v1/search/", methods=["POST"])
def search_databases():
    token = flask.request.args.get("provider_token", "")

    url_search = "https://api.notion.com/v1/search"
    url_db = "https://api.notion.com/v1/databases/"

    payload = {"filter": {"value": "database", "property": "object"}}
    headers = {
        "accept": "application/json",
        "Notion-Version": "2022-06-28",
        "content-type": "application/json",
        "authorization": f"Bearer {token}",
    }

    response = requests.post(url_search, json=payload, headers=headers)
    if response.status_code == 200:
        data = response.json()["results"]
        result = []
        for obj in data:
            db_id = obj["id"]
            response2 = requests.get(url_db + db_id)
            if response2.status_code == 200:
                try:
                    name = response2.json()["title"][0]["text"]["content"]
                except KeyError:
                    name = ""
                result.append({"name": name, "id": db_id})

        return flask.jsonify({"data": data})
    else:
        return flask.jsonify(make_err_response("Error in request")), 408


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


@noted.app.route("/api/v1/download/<filename>/", methods=["GET"])
def download_file(filename):
    filename = Path(filename)
    suffix = Path(filename).suffix
    if suffix == ".mp3":
        folder = noted.app.config["AUDIO_FOLDER"]
    else:
        folder = noted.app.config["VIDEO_FOLDER"]
    filepath = folder / filename
    return flask.send_from_directory(filepath, as_attachment=True), 200


@noted.app.route("/api/v1/predict/<filename>/<db_id>", methods=["GET"])
def predict(filename, db_id):
    filename = Path(filename)
    suffix = filename.suffix
    style = flask.request.args.get("style", Style.CONCISE, type=int)
    token = flask.request.args.get("provider_token", "")

    url = "https://api.notion.com/v1/pages"

    payload = {
        "parent": {"databasse_id": db_id},
        "properties": {
            "Name": {"title": [{"text": {"content": "Get Noted!"}}]}
        },
    }
    headers = {
        "accept": "application/json",
        "Notion-Version": "2022-06-28",
        "content-type": "application/json",
        "authorization": f"Bearer {token}",
    }

    if suffix == ".mp3":
        LOGGER.info("Starting prediction...")
        try:
            prompt = (
                noted.app.config["AUDIO_PROMPT_CONCISE"]
                if style == Style.CONCISE.value
                else noted.app.config["AUDIO_PROMPT_ELABORATE"]
            )
            model_response = noted.model.predict_audio(
                noted.app.config["AUDIO_FOLDER"] / filename,
                prompt,
                noted.app.config["MODEL"],
            )
            payload["children"] = model_response
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                url = response.json()["url"]
                return flask.jsonify({"url": url})
            return (
                flask.jsonify(make_err_response("Error with Notion")),
                408,
            )
        except (RetryError, ResourceExhausted) as e:
            return flask.jsonify(make_err_response("Error with Gemini")), 408

    return flask.jsonify({"hello": "world"})
    # else:
    #     predict_video(noted.app.config["VIDEO_FOLDER"] / filename)


def make_err_response(err):
    return {"error": err}


class Style(Enum):
    CONCISE = 0
    ELABORATE = 1

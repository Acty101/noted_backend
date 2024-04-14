"""Create a noted server."""

from flask import Flask
from flask_cors import CORS
from pathlib import Path
import shutil


# create flask instance
app = Flask(__name__)
CORS(app)
ROOT = Path(__file__).resolve().parent

# create folders
uploads = ROOT / Path("uploads")
# if uploads.exists() and uploads.is_dir():
#     shutil.rmtree(uploads)
# audio = uploads / Path("audio")
# video = uploads / Path("video")
# audio.mkdir(parents=True)
# video.mkdir(parents=True)


# configurations
app.config["UPLOAD_FOLDER"] = uploads
app.config["VIDEO_FOLDER"] = app.config["UPLOAD_FOLDER"] / Path("video")
app.config["AUDIO_FOLDER"] = app.config["UPLOAD_FOLDER"] / Path("audio")


# get prompt
with open(ROOT / Path("model", "prompt.txt"), "r") as prompt:
    app.config["AUDIO_PROMPT"] = prompt.read()

# get model
from noted.model import MODEL

app.config["MODEL"] = MODEL


import noted.api  # noqa: E402  pylint: disable=wrong-import-position

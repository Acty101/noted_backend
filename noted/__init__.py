"""Create a noted server."""

from flask import Flask
from pathlib import Path
import shutil

# create flask instance
app = Flask(__name__)
ROOT = Path(__file__).resolve().parent

# create folders
uploads = ROOT / Path("uploads")
if uploads.exists() and uploads.is_dir():
    shutil.rmtree(uploads)
audio = uploads / Path("audio")
video = uploads / Path("video")
audio.mkdir(parents=True)
video.mkdir(parents=True)


# configurations
app.config["UPLOAD_FOLDER"] = uploads
app.config["VIDEO_FOLDER"] = app.config["UPLOAD_FOLDER"] / Path("video")
app.config["AUDIO_FOLDER"] = app.config["UPLOAD_FOLDER"] / Path("audio")


import noted.api  # noqa: E402  pylint: disable=wrong-import-position

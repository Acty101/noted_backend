# import os
# from io import BytesIO

# from flask.testing import FlaskClient
# import pytest
# import noted

# @pytest.fixture
# def app(tmp_path: str) -> FlaskClient:
#     """Fixture to create a Flask app with a temporary upload folder."""
#     # Replace with your actual Flask application instance
#     noted.app.config["UPLOAD_FOLDER"] = tmp_path / "uploads"
#     with noted.app.test_client() as client:
#         yield client


# def test_upload_mp4_success(app: FlaskClient) -> None:
#     """Tests that the server successfully uploads an MP4 file."""
#     # Create a mock MP4 file with test data
#     test_data = b"This is some test video data"
#     test_file = BytesIO(test_data)
#     test_file.filename = "./tmp/example.mp4"

#     data = {"file": (test_file)}
#     print(data)
#     response = app.post(
#         "/api/v1/upload/", data=data, content_type="multipart/form-data"
#     )

#     assert response.status_code == 200


# import requests

# url = "http://localhost:9000/api/v1/upload/"
# filename = "./tmp/example.mp4"

# with open(filename, "rb") as f:
#     file_data = f.read()

# data = {"file": (filename, file_data)}
# response = requests.post(url, files=data)

# if response.status_code == 200:
#     print("File uploaded successfully!")
# else:
#     print(f"Upload failed: {response.status_code}")
#     print(response.text)

import noted

model_response = noted.model.predict_audio(
    str(noted.app.config["AUDIO_FOLDER"] / "68575ec1-54b1-43d2-a3ca-d663c25f3326example_out.mp3"),
    noted.app.config["AUDIO_PROMPT"],
    noted.app.config["MODEL"],
)
import flask
import noted


@noted.app.route("/api/v1/upload_file/", methods=["POST"])
def upload_file():
    pass


@noted.app.route("/api/v1/predict/", methods=["GET"])
def predict():
    pass

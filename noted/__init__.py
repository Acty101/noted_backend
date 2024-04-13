"""Create an index server."""

from flask import Flask

# create flask instance
app = Flask(__name__)

import noted.api  # noqa: E402  pylint: disable=wrong-import-position

SHELL := /bin/bash

debug:
	flask --app noted  --debug run --host 0.0.0.0 --port 8080

run:
	flask --app noted  run --host 0.0.0.0 --port 8080
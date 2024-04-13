SHELL := /bin/bash

run-debug:
	source .env
	flask --app noted  --debug run --host 0.0.0.0 --port 8080

run:
	source .env
	flask --app noted  run --host 0.0.0.0 --port 8080
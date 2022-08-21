default: lint test

lint: black flake8 isort mypy

black:
  poetry run black outbox_streaming

flake8:
  poetry run flake8 outbox_streaming

isort:
  poetry run isort outbox_streaming

mypy:
  poetry run mypy outbox_streaming

test:
  docker-compose up --detach db
  poetry run pytest -svvv
  docker-compose stop db
run:
	python3 ./src/rofehcloud/__main__.py

venv:
	python3 -m venv .venv

install:
	pip install -r requirements.txt

check:
	pre-commit run --all-files
	# -black .
	# -ruff .

build:
	python3 -m build

upload:
	python3 -m twine upload  dist/* --verbose

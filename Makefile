run:
	python3 rofehcloud.py

venv:
	python3 -m venv .venv

install:
	pip install -r requirements.txt


check:
	pre-commit run --all-files
	# -black .
	# -ruff .

run:
	PYTHONPATH="./:../common/" python3 main.py

venv:
	python3 -m venv .venv

install:
	pip install -r requirements.txt


check:
	-black .
	-ruff .

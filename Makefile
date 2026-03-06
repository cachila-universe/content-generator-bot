.PHONY: setup run dashboard test clean

setup:
	python scripts/setup.py

run:
	python scripts/start_bot.py

dashboard:
	python scripts/start_dashboard.py

test:
	python scripts/test_run.py

unittest:
	python -m pytest tests/ -v

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -name "*.pyc" -delete

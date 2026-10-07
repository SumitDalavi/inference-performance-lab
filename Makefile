.PHONY: setup dev clean

setup:
	uv pip install -r requirements.txt

dev:
	docker compose up -d
	uv run python mock_server.py &
	uv run python benchmark.py --config config/test.yaml
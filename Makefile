.PHONY: phoenix
phoenix:
	@echo "Running phoenix server"
	@uv run python -m phoenix.server.main --port 6006 --host 0.0.0.0 serve

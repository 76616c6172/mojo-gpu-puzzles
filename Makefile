.PHONY: deploy
deploy:
	@ modal deploy modal/app.py

.PHONY: run
puzzle:
	@ uv run modal/call.py

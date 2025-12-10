.PHONY: deploy
deploy:
	@ modal deploy modal/app.py

.PHONY: puzzle
puzzle:
	@ uv run modal/call.py

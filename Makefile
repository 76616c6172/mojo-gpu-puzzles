.PHONY: deploy
deploy:
	@ modal deploy modal/app.py

.PHONY: run
call:
	@ uv run modal/call.py

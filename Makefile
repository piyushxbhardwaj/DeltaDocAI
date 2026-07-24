.PHONY: help install test eval run docker-build docker-up

help:
	@echo "DeltaDoc AI Makefile"
	@echo "--------------------"
	@echo "make install      - Install backend dependencies"
	@echo "make test         - Run pytest suite"
	@echo "make eval         - Run quantitative AI evaluation scorecard"
	@echo "make run          - Run FastAPI dev server"
	@echo "make docker-up    - Build and launch Docker Compose stack"

install:
	pip install -r requirements.txt

test:
	pytest tests/ -v

eval:
	python -c "import asyncio; from src.api.dependencies import get_chat_engine; from src.eval.metrics import EvaluationSuite; print(asyncio.run(EvaluationSuite.run_full_evaluation([], get_chat_engine(), 'eval-session')))"

run:
	python main.py

docker-up:
	docker compose up --build -d

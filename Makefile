.PHONY: help install db-setup run test docker-up docker-down clean

help:
	@echo "TeamPulse - Available commands:"
	@echo "  make install    - Install Python dependencies"
	@echo "  make db-setup   - Setup PostgreSQL database"
	@echo "  make run        - Run application locally"
	@echo "  make test       - Run tests"
	@echo "  make docker-up  - Start Docker containers"
	@echo "  make docker-down - Stop Docker containers"
	@echo "  make clean      - Clean up files"

install:
	cd backend && pip install -r requirements.txt

db-setup:
	docker run -d --name teampulse-db \
		-e POSTGRES_DB=teampulse \
		-e POSTGRES_USER=teampulse \
		-e POSTGRES_PASSWORD=password \
		-p 5432:5432 \
		postgres:15-alpine
	@echo "Waiting for PostgreSQL to start..."
	@sleep 3
	psql postgresql://teampulse:password@localhost:5432/teampulse < database/schema.sql
	@echo "✅ Database setup complete!"

run:
	@echo "Starting TeamPulse..."
	@echo "App: http://localhost:3000"
	cd backend && python app.py

docker-up:
	docker-compose up -d
	@echo "✅ Docker containers started!"
	@echo "App: http://localhost:3000"
	@echo "View logs: docker-compose logs -f"

docker-down:
	docker-compose down

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.log" -delete

.PHONY: start stop restart logs clean

start:
	docker compose up -d --build
	pip install ./sdk

stop:
	docker compose down

restart: stop start

logs:
	docker compose logs -f

clean:
	docker compose down -v --rmi all
	pip uninstall -y openos 2>/dev/null || true

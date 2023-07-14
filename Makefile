include .env

.PHONY: help
help:
	@echo "=========================================================="
	@echo "build 		build all required container"
	@echo "setup 		run all required container"
	@echo "run 		run application"
	@#echo "test		run all tests"
	@echo "stop		stop all containers and shut down application"
	@echo "=========================================================="

.PHONY: local_run
local_run:
	@python3 main.py

.PHONY: test
test:
	@python3 -m pytest

.PHONY: local_setup
local_setup:
	@docker run -d --name dvwa --rm -it -p 80:80 vulnerables/web-dvwa &>/dev/null

	@# give Docker time to setup container
	@sleep 5

	@celery -q -A modules.task_queue worker &
	@sleep 2
	@echo "Setup is ready."

.PHONY: local_stop
local_stop:
	@docker stop dvwa &>/dev/null

.PHONY: build b
build b:
	@mkdir -p logs
	@docker compose build -q

.PHONY: setup s
setup s:
	@./setup_logs.sh
	@docker compose up dvwa worker flower redis -d &>/dev/null

.PHONY: run r
run r:
	@docker compose run --rm multitool

.PHONY: stop
stop:
	@docker compose down --volumes
	@whoami | xargs killall tail -u &>/dev/null

.PHONY: clean c
clean c:
	@docker image prune && docker volume prune
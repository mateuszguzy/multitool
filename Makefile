include .env

.PHONY: help
help:
	@echo "=========================================================="
	@echo "build 		build all required container"
	@echo "setup 		run all dependant containers"
	@echo "run 		run application"
	@echo "stop		stop all containers and shut down the application"
	@echo "tests		run all tests"
	@echo "=========================================================="

.PHONY: build b
build b:
	@mkdir -p logs
	@docker compose build -q

.PHONY: setup s
setup s:
	@docker compose up dvwa worker_main worker_logging worker_events flower redis -d
	@./setup_logs.sh

.PHONY: zap z
zap z:
	@docker compose up zap

.PHONY: run r
run r:
	@docker compose run --rm multitool

.PHONY: stop
stop:
	@docker compose down --volumes
	@whoami | xargs killall multitail -u &>/dev/null
	@tmux kill-session -t multitool_session

.PHONY: stop-m sm
stop-m sm:
	@tmux kill-session -t multitool_session

.PHONY: clean c
clean c:
	@docker image prune && docker volume prune
	@docker system prune

.PHONY: tests t
tests t:
	@docker compose -f "docker-compose.tests.yaml" build -q
	@docker compose -f "docker-compose.tests.yaml" up test-dvwa test-worker redis -d &>/dev/null
	@sleep 5
	@docker compose -f "docker-compose.tests.yaml" up test-multitool
	@docker compose -f "docker-compose.tests.yaml" down --volumes &>/dev/null

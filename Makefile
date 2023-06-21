include .env

.PHONY: help
help:
	@echo "=========================================================="
	@echo "setup 		prepare everything for app to run properly"
	@echo "run 		run application"
	@echo "test		run all tests"
	@echo "stop		stop processes running in background"
	@echo "=========================================================="

.PHONY: run
run:
	@python3 main.py

.PHONY: test
test:
	@python3 -m pytest

.PHONY: setup
setup:
	@docker run -d --name dvwa --rm -it -p 80:80 vulnerables/web-dvwa &>/dev/null

	@# give Docker time to setup container
	@sleep 5

	@celery -q -A modules.task_queue worker &
	@# NOT WORKING ON MAC - check on LINUX (cannot assign IP other than 127.0.0.1 and there's conflict between DVWA / Flower)
	@#celery -A modules.task_queue flower  --address=$(CELERY_FLOWER_ADDRESS) --port=$(CELERY_FLOWER_PORT) worker
	@sleep 2
	@echo "Setup is ready."

.PHONY: stop
stop:
	@docker stop dvwa &>/dev/null

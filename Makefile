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
	@docker run -d --name rabbitmq --rm -p 5672:5672 rabbitmq &>/dev/null

	@# give Docker time to setup container
	@sleep 10

	@# setup RabbitMQ
	@docker exec -it rabbitmq sh -c "rabbitmqctl add_user $(RABBITMQ_USER) $(RABBITMQ_PASSWORD)"
	@docker exec -it rabbitmq sh -c "rabbitmqctl add_vhost $(RABBITMQ_VHOST)"
	@docker exec -it rabbitmq sh -c "rabbitmqctl set_user_tags $(RABBITMQ_USER) mytag"
	@docker exec -it rabbitmq sh -c "rabbitmqctl set_permissions -p $(RABBITMQ_VHOST) $(RABBITMQ_USER) '.*' '.*' '.*'"

	@celery -A modules.task_queue worker
	@# NOT WORKING ON MAC - check on LINUX (cannot assign IP other than 127.0.0.1 and there's conflict between DVWA / Flower)
	@#celery -A modules.task_queue flower  --address=$(CELERY_FLOWER_ADDRESS) --port=$(CELERY_FLOWER_PORT) worker

.PHONY: stop
stop:
	@docker stop dvwa &>/dev/null
	@docker stop rabbitmq &>/dev/null

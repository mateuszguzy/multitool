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

.PHONY: stop
stop:
	@docker stop dvwa &>/dev/null

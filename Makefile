.PHONY: help
help:
	@echo "==============================="
	@echo "run 		run application"
	@echo "test		run all tests"
	@echo "==============================="

.PHONY: run
run:
	python3 main.py

.PHONY: test
test:
	python3 -m pytest

.PHONY: default
default: help

.PHONY: help
help:
	@echo "make help		Show this help message"
	@echo "make clean-pyc	Clean pyc files from every directory"
	@echo "make venv		Create a virtualenv in .venv directory"

.PHONY: clean-pyc
clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

.PHONY: venv
venv:
	python3 -m venv .venv && \
		source .venv/bin/activate && \
		pip install -r requirements.txt


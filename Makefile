venv:
	poetry install

.PHONY: install-hooks
install-hooks: venv
	poetry run pre-commit install

.PHONY: test
test:
	poetry install


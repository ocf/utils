.PHONY: test
test: venv
	venv/bin/pre-commit install
	venv/bin/pre-commit run --all-files

venv: Makefile
	vendor/venv-update \
		venv= venv -ppython3 \
		install= -r requirements-dev.txt

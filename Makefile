.PHONY: test
test:
	pre-commit install
	pre-commit run --all-files

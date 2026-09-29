VENV ?= .venv
MAP ?= data/maps/easy/01_linear_path.txt

$(VENV): pyproject.toml
	uv sync

run: install
	uv run python -m src $(MAP)

install: $(VENV)

debug: install
	uv run python -m pdb -m src $(MAP)

re: fclean install

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .mypy_cache -exec rm -rf {} +
	find . -type d -name output -exec rm -rf {} +
	find . -type d -name stdout -exec rm -rf {} +
	find . -type d -name stderr -exec rm -rf {} +

fclean: clean
	rm -rf .venv

flake8: install
	echo Running Flake8
	uv run python -m flake8 . --exclude=$(VENV)

mypy: install
	echo Running Mypy
	uv run python -m mypy . \
		--warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs \
		--exclude \
		$(VENV);

lint: install flake8 mypy

mypy-strict: install
	echo Running Mypy
	uv run python -m mypy . --strict --exclude $(VENV)

lint-strict: flake8 mypy-strict

black: install
	uv run python -m black --line-length 79 .

.PHONY: run install debug re clean fclean flake8 mypy lint mypy-strict lint-strict black

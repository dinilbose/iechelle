.PHONY: help install test docs build clean

# Get the currently active Python interpreter from Poetry's environment
# This might be more robust if `poetry run which python` was guaranteed,
# but `poetry run python` itself should use the correct interpreter.
PYTHON := poetry run python

# Sphinx command using poetry run
SPHINXBUILD := poetry run sphinx-build
SPHINXOPTS :=
SPHINXSOURCEDIR := docs/source
SPHINXBUILDDIR := docs/build

help:
	@echo "Makefile for iEchelle development"
	@echo ""
	@echo "Usage:"
	@echo "  make install    to install dependencies"
	@echo "  make test       to run unit tests"
	@echo "  make docs       to build HTML documentation"
	@echo "  make build      to build the package"
	@echo "  make clean      to remove build artifacts and temporary files"
	@echo ""

install:
	@echo "Installing dependencies using Poetry..."
	poetry install

test:
	@echo "Running unit tests with pytest..."
	poetry run pytest tests/

docs:
	@echo "Building Sphinx HTML documentation..."
	@echo "Source directory: $(SPHINXSOURCEDIR)"
	@echo "Build directory: $(SPHINXBUILDDIR)"
	$(SPHINXBUILD) -b html $(SPHINXSOURCEDIR) $(SPHINXBUILDDIR)/html $(SPHINXOPTS)
	@echo "Documentation built in $(SPHINXBUILDDIR)/html/index.html"

build:
	@echo "Building package using Poetry..."
	poetry build

clean:
	@echo "Cleaning up build artifacts and temporary files..."
	# Remove Python cache and compiled files
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} +
	# Remove pytest cache
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	# Remove Sphinx build directory
	rm -rf $(SPHINXBUILDDIR)
	# Remove Poetry build artifacts
	rm -rf dist/
	rm -rf build/ # General build directory, if any created outside Poetry's dist
	# Remove .DS_Store files (macOS specific)
	find . -name '.DS_Store' -type f -delete
	# Remove .mypy_cache if it exists
	rm -rf .mypy_cache/
	# Remove any .egg-info directories
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	@echo "Clean up complete."

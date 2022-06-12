#!/bin/bash

VIRTUALENV_DIR=.venv

echo "Creating virtualenv at <CURRENT_DIR>/.venv"
python3 -m venv $VIRTUALENV_DIR
echo "Created virtualenv"

echo "Initializing project with poetry"
poetry init -n --author "pozalabs <contact@pozalabs.com>" --dev-dependency pre-commit
source $VIRTUALENV_DIR/bin/activate

poetry install
echo "Initialized project with poetry"

cat >> pyproject.toml << EOF

[tool.black]
line-length = 100
target-version = ['py39']
exclude = '''
/(
    \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | _build
  | buck-out
  | build
  | dist
)/
'''

[tool.isort]
multi_line_output = 3
include_trailing_comma = true
force_grid_wrap = 0
use_parentheses = true
ensure_newline_before_comments = true
line_length = 100
EOF

echo "Added pre-commit configurations"

echo "Installing pre-commit"
pre-commit install
echo "Installed pre-commit"

echo "Poetry setup finished"
echo "Type package name. This will create python package with <PACKAGE_NAME>"
read PACKAGE_NAME
mkdir $PACKAGE_NAME && touch $PACKAGE_NAME/__init__.py

echo "Created python package named $PACKAGE_NAME"

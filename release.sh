#!/usr/bin/env bash
set -euo pipefail

python setup.py sdist
twine upload dist/*

#!/bin/bash
set -e

coverage run --source='/app' manage.py test -v 3 --noinput
coverage html -d htmlcov
coverage xml
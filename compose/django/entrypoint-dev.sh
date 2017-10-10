#!/bin/bash
set -e
cmd="$@"

bash /wait-for-it.sh postgres:5432

exec $cmd

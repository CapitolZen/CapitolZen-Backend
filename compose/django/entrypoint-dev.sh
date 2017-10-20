#!/bin/bash
set -e
cmd="$@"

bash /wait-for-it.sh elasticsearch:9200

exec $cmd

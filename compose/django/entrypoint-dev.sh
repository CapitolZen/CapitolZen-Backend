#!/bin/bash
set -e
cmd="$@"

bash /wait-for-it.sh elasticsearch1:9200

exec $cmd

#!/bin/bash -x
current_path=$(pwd)
######################### For Server ########################
nohup python $current_path/manage.py runserver 0:3000 > $current_path/logs/myapp.log 2>&1 &
exec "$@"

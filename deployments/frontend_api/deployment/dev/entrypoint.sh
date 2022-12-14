#!/bin/sh
python3 manage.py create_db
# python3 -m gunicorn --reload --bind 0.0.0.0:5000 'app:create_app()'
python3 manage.py run -h 0.0.0.0

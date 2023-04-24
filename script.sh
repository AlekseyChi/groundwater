#!/bin/bash
cd /usr/src/app/
# Collect static files
echo "Collect static files"
python3 manage.py collectstatic --noinput;

# Apply database migrations
python3 manage.py makemigrations darcy_app;
echo "Apply database migrations"
python3 manage.py migrate;
echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'pass')" | python3 manage.py shell
python3 manage.py loaddata darcy_app/dict_data.json;
gunicorn darcy.wsgi:application --bind 0.0.0.0:8000 --reload --limit-request-line 8100;

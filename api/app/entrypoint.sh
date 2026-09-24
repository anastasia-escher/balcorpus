#!/usr/bin/env bash

PORT=5000

python manage.py collectstatic --noinput

python manage.py wait_for_db
python manage.py migrate
python manage.py initadmin

if [ "$DJANGO_DEBUG" == "True" ]; then
  python manage.py runserver 0.0.0.0:${PORT}
else
  gunicorn bcorpus.asgi:application \
    --log-file - \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --timeout 300 \
    --bind 0.0.0.0:${PORT}
fi

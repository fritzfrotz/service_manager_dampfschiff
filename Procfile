web: gunicorn dampfschiff.wsgi --log-file -
worker: celery -A dampfschiff worker --loglevel=info
beat: celery -A dampfschiff beat --loglevel=info

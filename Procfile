release: python manage.py makemigrations core && migrations -g
web: gunicorn lineage.wsgi --log-file -
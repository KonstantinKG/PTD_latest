web: daphne PTD.asgi:application --port $PORT --bind 0.0.0.0 -v2
worker: python manage.py runworker channels --settings=PTD.settings -v2
web: bin/start-pgbouncer-stunnel daphne hellodjango.wsgi
# PTD
Platinum Dragons Call of Duty Gamis WebSite

Если не нужен чат пиши  web: gunicorn PTD.wsgi --log-file - в Procfile

Если нужен
release: python manage.py migrate
web: daphne PTD.asgi:application --port $PORT --bind 0.0.0.0 -v2
worker: python manage.py runworker channels --settings=PTD.settings -v2

Ссылка на админку https://localhost/admin

# Docker-compose

**1 Builds and runs app**
```commandline
docker-compose up --build --wait
```

**2 Applies migrations**
```commandline
docker-compose exec web python manage.py migrate
```

**3 Creates superuser**
```commandline
docker-compose exec web python manage.py createsuperuser
```

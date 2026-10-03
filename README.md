# campus-security-analytics

**Camera analytics platform: video surveillance with face and licence-plate recognition.**

Django web application for video surveillance analytics: it pulls a live stream
from IP cameras, detects faces and licence plates in the frames, matches them
against a database of known persons and cars, and shows the result on an
internal dashboard. Detection runs in background workers (Celery + Redis), so
the HTTP request that starts a camera never blocks on computer vision.

Built for the All-Russian Hackathon (2022) and reworked afterwards.

## Features

- **Camera management** — add, edit and remove IP cameras (host, port, RTSP credentials)
- **Live video** — MJPEG stream in the browser straight from the camera, no plugin needed
- **Face recognition** — `dlib` + `face_recognition`, k-NN classifier, faces marked on the frame
- **Licence plate recognition** — OpenCV + Haar cascade (`haarcascade_russian_plate_number.xml`)
- **Access decisions** — person + plate are matched against the database, the barrier/door
  command is returned only when both are known
- **Person and car database** — CRUD, photo upload per person, Django admin
- **REST API** — Django REST Framework with JWT auth for persons, cars, cameras and event logs
- **API documentation** — OpenAPI schema and Swagger UI at `/api/docs/`
- **Event log** — every entry is written to `EntryPersonLog` / `EntryCarLog`
- **Async processing** — recognition and model training run as Celery tasks
- **Tested** — API test suite covering auth, permissions, pagination and normalisation
- **Hardened admin** — `django-axes` brute-force protection, honeypot admin panel
  (`/admin/` is a trap, the real one is at `/secret/`)

## Stack

| Layer | Technology |
|---|---|
| Backend | Python 3 · Django 3.2 · Django REST Framework 3.14 · SimpleJWT · drf-spectacular |
| CV / ML | OpenCV · dlib · face_recognition · scikit-learn · TensorFlow/Keras |
| Data | PostgreSQL (falls back to SQLite) · Redis (broker + result backend) |
| Frontend | Django templates · Bootstrap 5 · jQuery · Chart.js |
| Infra | Docker Compose (PostgreSQL, Redis, app, workers) · Gunicorn · WhiteNoise |

## Getting started

### 1. Environment

```bash
git clone https://github.com/Wildamager/campus-security-analytics.git
cd campus-security-analytics
python -m venv venv                 # Python 3.10, the versions in requirements.txt target it
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configuration

```bash
cp .env.example .env            # Windows: copy .env.example .env
```

Generate a real secret key:

```bash
python -c "from django.core.management.utils import get_random_secret_key as k; print(k())"
```

`.env` must never be committed — it is in `.gitignore`, and only `.env.example` is
tracked in the repository.

### 3. Infrastructure

Redis is needed for Celery:

```bash
docker compose up -d redis
```

The whole stack can run in containers as well — PostgreSQL, Redis, the Django
app under Gunicorn and both Celery workers:

```bash
docker compose up -d --build
```

`POSTGRES_PASSWORD` must be set in `.env` before that, the image compiles
`dlib` and `face_recognition` on the first build, and the dashboard is then on
http://127.0.0.1:8000/.

### 4. Database and superuser

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

PostgreSQL is used when `POSTGRES_DB` is set in `.env`; otherwise SQLite is used
so the project starts with zero external services.

### 5. Run

```bash
python manage.py runserver
celery -A backend worker -l info        # terminal 1 — recognition tasks
celery -A backend beat -l info          # terminal 2 — periodic tasks
```

Open http://127.0.0.1:8000/ and sign in.

### Environment variables

| Variable | Default | Purpose |
|---|---|---|
| `SECRET_KEY` | — | required, Django secret key |
| `DEBUG` | `False` | debug mode |
| `ALLOWED_HOSTS` | `127.0.0.1` | space-separated hosts |
| `CELERY_BROKER_REDIS_URL` | `redis://localhost:6379` | broker |
| `CELERY_RESULT_BACKEND` | `redis://localhost:6379` | result backend |
| `POSTGRES_DB` / `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_HOST` / `POSTGRES_PORT` | — | PostgreSQL connection; empty `POSTGRES_DB` → SQLite |
| `AXES_FAILURE_LIMIT` | `4` | login attempts before lockout |
| `AXES_COOLOFF_TIME` | `2` | lockout duration, hours |

The API and the dashboard share one origin, so no CORS configuration is needed.
Serving the API from a separate frontend would mean adding `django-cors-headers`
and a real origin list.

## REST API

All endpoints live under `/api/` and require an authenticated user. Get a token
pair with your Django credentials:

```bash
curl -X POST http://127.0.0.1:8000/api/auth/token/ \
     -H 'Content-Type: application/json' \
     -d '{"username": "admin", "password": "your-password"}'
```

```bash
curl http://127.0.0.1:8000/api/persons/ -H 'Authorization: Bearer <access>'
```

| Endpoint | Methods | Notes |
|---|---|---|
| `/api/auth/token/` | POST | JWT pair (`access`, `refresh`) |
| `/api/auth/token/refresh/` | POST | new access token from a refresh token |
| `/api/persons/` | GET, POST, PATCH, DELETE | `?search=` over name, email, contact; email is lowercased, photo optional |
| `/api/cars/` | GET, POST, PATCH, DELETE | `?search=` over owner, plate, brand; plate is uppercased without spaces |
| `/api/cameras/` | GET, POST, PATCH, DELETE | `login` and `password` are write-only and never returned |
| `/api/logs/persons/`, `/api/logs/cars/` | GET | read-only event log, newest first |
| `/api/summary/` | GET | counters for the dashboard header |
| `/api/docs/` | GET | Swagger UI |
| `/api/schema/` | GET | raw OpenAPI schema |

Lists are paginated (25 per page) with `?page=` and `?page_size=`.

## Tests

The API test suite runs on SQLite, so no database or Redis is needed:

```bash
python manage.py test apps.data
```

It covers token issuing, anonymous access rejection, bearer authorisation,
pagination, search, field normalisation, write-only camera credentials,
read-only logs and the summary endpoint. Regenerate the OpenAPI schema with
`python manage.py spectacular --file schema.yml`.

## Project structure

```text
.
├── apps/
│   ├── camerastream/     # cameras, live stream, recognition tasks, CV models
│   └── data/             # persons and cars database, CRUD, forms, REST API
├── backend/              # settings, urls, celery app
├── static/               # admin assets, dashboard css/js
├── templates/            # dashboard, database, auth pages
├── Dockerfile            # app image: Python 3.10, ML deps, Gunicorn
├── docker-compose.yml    # PostgreSQL, Redis, app, Celery worker and beat
├── manage.py
└── requirements.txt
```

## Notes and limitations

- The face model (`*.clf`) and the 95 MB landmark predictor (`*.dat`) are
  git-ignored and no longer tracked. After cloning, put the predictor in
  `apps/camerastream/shape_predictor_68_face_landmarks.dat` (it also ships with
  the `face_recognition_models` package) and run the training task to
  regenerate the classifier.
- CV dependencies (`dlib`, `face_recognition`, TensorFlow) need CMake and a C++
  toolchain on Linux; on Windows use prebuilt wheels.
- RTSP stream URLs in `apps/camerastream/camera.py` are device-specific and are
  meant to be configured per camera in the dashboard.
- Plate recognition uses the Russian Haar cascade
  (`haarcascade_russian_plate_number.xml`); other locales need another XML.

## Roadmap

- [x] Camera management + live MJPEG stream
- [x] Face recognition and plate recognition
- [x] Celery workers for recognition and training
- [x] PostgreSQL support and a Docker Compose stack
- [x] REST API with JWT authentication and OpenAPI docs
- [x] API test suite
- [ ] Separate frontend (React) consuming the API
- [ ] CI on push

## License

[MIT](LICENSE)

---

## RU

Веб-приложение на Django для аналитики с камер видеонаблюдения: живой видеопоток
с IP-камер, распознавание лиц и автомобильных номеров, сверка с базой людей и
машин, выдача команды на открытие барьера. Распознавание вынесено в Celery-задачи,
интерфейс — Django-шаблоны и Bootstrap. Есть REST API на Django REST Framework
с JWT-авторизацией и Swagger по адресу `/api/docs/`, покрытый тестами.
Поддерживаются PostgreSQL и Redis, есть защита админки (django-axes, honeypot).
Лицензия MIT.
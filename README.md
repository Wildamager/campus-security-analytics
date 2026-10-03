# Camera Analytics Platform

Django web application for video surveillance analytics: it pulls a live stream
from IP cameras, detects faces and licence plates in the frames, matches them
against a database of known persons and cars, and shows the result on an
internal dashboard. Detection runs in background workers (Celery + Redis), so
the HTTP request that starts a camera never blocks on computer vision.

Built for the All-Russian Hackathon (2022) and reworked afterwards.

<!-- Screenshots: put them in docs/screenshots/ and uncomment
![Dashboard](docs/screenshots/dashboard.png)
-->

## Features

- **Camera management** — add, edit and remove IP cameras (host, port, RTSP credentials)
- **Live video** — MJPEG stream in the browser straight from the camera, no plugin needed
- **Face recognition** — `dlib` + `face_recognition`, k-NN classifier, faces marked on the frame
- **Licence plate recognition** — OpenCV + Haar cascade (`haarcascade_russian_plate_number.xml`)
- **Access decisions** — person + plate are matched against the database, the barrier/door
  command is returned only when both are known
- **Person and car database** — CRUD, photo upload per person, Django admin
- **Event log** — every entry is written to `EntryPersonLog` / `EntryCarLog`
- **Async processing** — recognition and model training run as Celery tasks
- **Hardened admin** — `django-axes` brute-force protection, honeypot admin panel
  (`/admin/` is a trap, the real one is at `/secret/`)

## Stack

| Layer | Technology |
|---|---|
| Backend | Python 3 · Django 3.2 · Celery 5 · Django REST-style views |
| CV / ML | OpenCV · dlib · face_recognition · scikit-learn · TensorFlow/Keras |
| Data | PostgreSQL (falls back to SQLite) · Redis (broker + result backend) |
| Frontend | Django templates · Bootstrap 5 · jQuery · Chart.js |
| Infra | Docker (Redis service) · Gunicorn-ready · Linux |

## Getting started

### 1. Environment

```bash
git clone https://github.com/Wildamager/campus-security-analytics.git
cd campus-security-analytics
python -m venv venv
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
| `CORS_ORIGIN_WHITELIST` | `127.0.0.1:3000` | allowed frontend origins |

## Project structure

```text
.
├── apps/
│   ├── camerastream/     # cameras, live stream, recognition tasks, CV models
│   └── data/             # persons and cars database, CRUD, forms
├── backend/              # settings, urls, celery app
├── static/               # admin assets, dashboard css/js
├── templates/            # dashboard, database, auth pages
├── docker-compose.yml    # Redis service
├── manage.py
└── requirements.txt
```

## Notes and limitations

- The face model (`trained_model.clf`) and the landmark predictor (`.dat`, ~100 MB)
  are not kept in the repository — the training task regenerates them.
- CV dependencies (`dlib`, `face_recognition`, TensorFlow) need CMake and a C++
  toolchain on Linux; on Windows use prebuilt wheels.
- RTSP stream URLs in `apps/camerastream/camera.py` are device-specific and are
  meant to be configured per camera in the dashboard.

## Roadmap

- [x] Camera management + live MJPEG stream
- [x] Face recognition and plate recognition
- [x] Celery workers for recognition and training
- [x] PostgreSQL support and Docker for Redis
- [ ] REST API with token authentication
- [ ] React dashboard consuming the API
- [ ] Tests and CI on push

## License

[MIT](LICENSE)

---

## RU

Веб-приложение на Django для аналитики с камер видеонаблюдения: живой видеопоток
с IP-камер, распознавание лиц и автомобильных номеров, сверка с базой людей и
машин, выдача команды на открытие барьера. Распознавание вынесено в Celery-задачи,
интерфейс — Django-шаблоны и Bootstrap. Поддерживаются PostgreSQL и Redis,
есть защита админки (django-axes, honeypot). Лицензия MIT.
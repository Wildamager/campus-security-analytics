FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# dlib and face_recognition are compiled from their sdists, so a C++ toolchain
# and CMake are required. libgl1/libglib2.0-0 are the runtime libraries OpenCV
# and dlib link against.
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        build-essential \
        cmake \
        git \
        libgl1 \
        libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./
# gunicorn is only used in the container, it is not part of the local setup
RUN pip install --no-cache-dir -r requirements.txt gunicorn==21.2.0

COPY . .

EXPOSE 8000

CMD ["gunicorn", "backend.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]

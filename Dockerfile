# Stage 1: compile Tailwind CSS (build-time only, not in the final image)
FROM node:20-slim AS css
WORKDIR /build
COPY package.json package-lock.json ./
RUN npm ci
COPY app/templates ./app/templates
COPY app/static/css/input.css ./app/static/css/input.css
RUN npm run build-css

# Stage 2: the actual runtime image
FROM python:3.12-slim
WORKDIR /app

# exiftool is a system binary the app shells out to (metadata_service.py),
# not a Python package, so it has to be installed at the OS level.
RUN apt-get update \
    && apt-get install -y --no-install-recommends libimage-exiftool-perl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
COPY --from=css /build/app/static/css/app.css ./app/static/css/app.css

ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=run.py

# Run pending migrations, then start gunicorn. Railway supplies $PORT.
# --timeout 300: the admin /sync route makes one Cloudinary Admin API call
# per photo (sequentially), so a bulk sync of many photos can take well
# past gunicorn's 30s default and get killed mid-request.
# --workers 2: so a long-running sync doesn't block the gallery for everyone
# else on the single-worker default.
CMD flask db upgrade && exec gunicorn run:app --bind 0.0.0.0:${PORT:-8000} --workers 2 --timeout 300

# Photography Website

Personal photography portfolio. Flask + PostgreSQL + Cloudinary, keywords sourced from Lightroom Classic exports. See [PROJECT_SPEC.md](PROJECT_SPEC.md) for the full design.

## Local setup

1. Python deps:
   ```
   python -m venv .venv
   .venv\Scripts\pip install -r requirements.txt
   ```

2. Front-end deps (Tailwind CLI):
   ```
   npm install
   npm run watch-css
   ```

3. Install exiftool (used to read Lightroom's embedded keywords/EXIF from exported JPEGs) and make sure it's on PATH:
   ```
   winget install oliverbetz.ExifTool
   ```
   or download from https://exiftool.org. If it lives somewhere not on PATH, set `EXIFTOOL_PATH` in `.env` to the full executable path.

4. Copy `.env.example` to `.env` and fill in Cloudinary credentials.

5. Set an admin password. Generate a hash and put it in `.env` as `ADMIN_PASSWORD_HASH`:
   ```
   .venv\Scripts\python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('your-password'))"
   ```
   `ADMIN_USERNAME` defaults to `admin`. `/admin` routes are inaccessible until `ADMIN_PASSWORD_HASH` is set.

6. Start local PostgreSQL (Docker Desktop required):
   ```
   docker compose up -d
   ```

7. Run migrations:
   ```
   set FLASK_APP=run.py
   flask db migrate -m "initial schema"
   flask db upgrade
   ```

8. Run the app:
   ```
   flask run
   ```

## Status

Working vertical slice (spec §42/§43, tasks 1–14): upload a JPEG at `/admin/upload` → exiftool reads title/description/date/camera/lens/keywords (flat + Lightroom hierarchical) → image uploaded to Cloudinary → `Photo` row created → keywords get-or-created and linked (hierarchy preserved via `parent_id`) → photo appears at `/` → clicking a keyword filters the gallery via `/?keyword=<slug>`. Duplicate-filename uploads are caught and require confirmation. Verified with an in-memory-SQLite smoke test exercising the full upload → gallery → filter path (not committed — ad hoc, rerun manually if you touch this flow), and with a real upload through the running app.

`/admin` now requires a session login (§26) — single admin user, username/password-hash from env vars, no self-serve registration.

Not yet built: richer multi-file/drag-and-drop upload UI (§22, v2), lightbox instead of a full photo page (§17), multi-keyword AND filtering (§18, v3), pagination (§29), Railway deployment + Dockerfile for exiftool.

Render deployment checklist and exact commands

1) Required Python packages to add to `requirements.txt` (append these lines):

gunicorn
dj-database-url
whitenoise
psycopg2-binary

2) Local test commands (run before push):

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn school_project.wsgi
```

3) Render dashboard steps summary:
- Create a Render account and connect your Git provider (GitHub/GitLab).
- In Render: New → PostgreSQL → create managed DB → copy `DATABASE_URL`.
- In Render: New → Web Service → connect repo and branch.
- Set Environment Variables in the Web Service settings:
  - `DATABASE_URL` (from the managed Postgres)
  - `DJANGO_SECRET_KEY` (a long secret)
  - `DJANGO_DEBUG` = `False`
  - `DJANGO_ALLOWED_HOSTS` = your-render-service.onrender.com
- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn school_project.wsgi --log-file -`
- Post Deploy Command: `python manage.py migrate && python manage.py collectstatic --noinput`

4) Media uploads:
- Use S3/Spaces/Cloudinary for `MEDIA_URL` — Render instances are ephemeral.

5) If you want me to finish these repo edits and run tests locally, tell me to proceed and provide permission to push changes.

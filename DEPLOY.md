# BOT MATRIX Backend — Deploy Anywhere

## Railway
1. New Project → Deploy from GitHub repo
2. Set env: SECRET_KEY, BASE_URL, CORS_ORIGINS
3. Optional Postgres → DATABASE_URL
4. Health: GET /api/health

## Render
Use render.yaml or Docker. Same env vars.

## VPS
```bash
cp .env.example .env
docker compose up -d --build
```

## Local
```bash
python run.py
```

BASE_URL must be HTTPS for Telegram webhooks.
Frontend: send Authorization: Bearer <token> from login.

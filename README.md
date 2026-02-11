# FastAPI + Vue + SQLite (Docker Compose multi-env)

Projet pédagogique minimal pour expliquer la différence entre **variables d'environnement non sensibles** et **secrets** montés via fichiers, avec trois environnements (dev/staging/prod) qui peuvent tourner sur la **même machine**.

## Structure

- `backend/main.py` : un seul fichier FastAPI
- `frontend/src/App.vue` : un seul composant Vue
- `compose.yml` + `compose.dev.yml` + `compose.staging.yml` + `compose.prod.yml`
- `.env.*.example` : exemples de variables non sensibles
- `secrets.example/` : exemples de secrets (fichiers)

## Variables vs secrets

- **Variables non sensibles** : dans `.env.*` (ex: `DATABASE_URL`, `VITE_API_URL`, `LOG_LEVEL`)
- **Secrets** : dans des fichiers montés (ex: `./secrets/<env>/api_token_secret.txt` monté vers `/run/secrets/api_token_secret`)
- Exemple de secret “DB password” simulé : `./secrets/<env>/db_password.txt` monté vers `/run/secrets/db_password`

## Préparation

1. Copier les `.env` depuis les exemples:

```bash
cp .env.dev.example .env.dev
cp .env.staging.example .env.staging
cp .env.prod.example .env.prod
```

2. Copier les secrets:

```bash
cp -r secrets.example secrets
```

## Lancer les environnements

### Dev (reload + Vite dev server)

```bash
docker compose --env-file .env.dev -f compose.yml -f compose.dev.yml up --build
```

- Frontend: http://localhost:5173
- Backend: http://localhost:8000/api/health

### Staging

```bash
docker compose --env-file .env.staging -f compose.yml -f compose.staging.yml up -d --build
```

- Frontend: http://localhost:5174
- Backend: http://localhost:8001/api/health

### Prod

```bash
docker compose --env-file .env.prod -f compose.yml -f compose.prod.yml up -d --build
```

- Frontend: http://localhost:5175
- Backend: http://localhost:8002/api/health

### Staging + Prod en même temps (1 seule machine)

Les ports étant distincts, vous pouvez lancer les deux stacks en parallèle.

## Tester avec curl

### Health

```bash
curl http://localhost:8000/api/health
curl http://localhost:8001/api/health
curl http://localhost:8002/api/health
```

### Lire les items

```bash
curl http://localhost:8000/api/items
curl http://localhost:8001/api/items
```

### Ajouter un item (nécessite X-Token)

```bash
curl -X POST http://localhost:8000/api/items \
  -H 'Content-Type: application/json' \
  -H 'X-Token: DEV_DEMO_SECRET' \
  -d '{"name":"hello dev"}'

curl -X POST http://localhost:8001/api/items \
  -H 'Content-Type: application/json' \
  -H 'X-Token: STAGING_DEMO_SECRET' \
  -d '{"name":"hello staging"}'
```

## Notes pédagogiques

- Le frontend utilise `import.meta.env.VITE_API_URL`.
- En **staging/prod**, `VITE_API_URL` est injecté **au build** via `build.args` dans `compose.*.yml` et `ARG` dans `frontend/Dockerfile`.
- Le backend lit le secret depuis `/run/secrets/api_token_secret` (monté en read-only).
- Le “DB password” simulé est lu depuis `/run/secrets/db_password` (monté en read-only).

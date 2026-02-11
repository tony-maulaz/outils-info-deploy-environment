# FastAPI + Vue + SQLite (Docker Compose multi-env)

Projet pédagogique minimal pour expliquer la différence entre **variables d'environnement non sensibles** et **secrets** montés via fichiers, avec trois environnements (dev/staging/prod) qui peuvent tourner sur la **même machine**.

## Structure

- `backend/main.py` : un seul fichier FastAPI
- `frontend/src/App.vue` : un seul composant Vue
- `compose.yml` + `compose.dev.yml` + `compose.staging.yml` + `compose.prod.yml`
- `docker/nginx/nginx.conf` : reverse proxy pour staging/prod
- `.env.*.example` : exemples de variables non sensibles
- `secrets.example/` : exemples de secrets (fichiers)

## Variables vs secrets

- **Variables non sensibles** : dans `.env.*` (ex: `DATABASE_URL`, `VITE_API_URL`, `LOG_LEVEL`)
- **Secrets** : dans des fichiers montés (ex: `./secrets/<env>/api_token_secret.txt` monté vers `/run/secrets/api_token_secret`)

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

3. Ajouter les hostnames locaux (Linux/macOS):

```bash
sudo sh -c 'echo "127.0.0.1 staging.localhost" >> /etc/hosts'
sudo sh -c 'echo "127.0.0.1 prod.localhost" >> /etc/hosts'
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

- http://staging.localhost

### Prod

```bash
docker compose --env-file .env.prod -f compose.yml -f compose.prod.yml up -d --build
```

- http://prod.localhost

### Staging + Prod en même temps (1 seule machine)

Pour isoler les stacks, utilisez `COMPOSE_PROJECT_NAME` et **un seul reverse proxy**.

1. Démarrer staging **avec** proxy:

```bash
COMPOSE_PROJECT_NAME=myapp_staging docker compose --env-file .env.staging -f compose.yml -f compose.staging.yml up -d --build
```

2. Démarrer prod **sans** proxy (le proxy de staging routtera vers prod):

```bash
COMPOSE_PROJECT_NAME=myapp_prod docker compose --env-file .env.prod -f compose.yml -f compose.prod.yml up -d --build --scale reverse_proxy=0
```

Le reverse proxy (port 80) route:
- `staging.localhost` -> `frontend_staging` + `backend_staging`
- `prod.localhost` -> `frontend_prod` + `backend_prod`

## Tester avec curl

### Health

```bash
curl http://localhost:8000/api/health
curl http://staging.localhost/api/health
curl http://prod.localhost/api/health
```

### Lire les items

```bash
curl http://localhost:8000/api/items
curl http://staging.localhost/api/items
```

### Ajouter un item (nécessite X-Token)

```bash
curl -X POST http://localhost:8000/api/items \
  -H 'Content-Type: application/json' \
  -H 'X-Token: DEV_DEMO_SECRET' \
  -d '{"name":"hello dev"}'

curl -X POST http://staging.localhost/api/items \
  -H 'Content-Type: application/json' \
  -H 'X-Token: STAGING_DEMO_SECRET' \
  -d '{"name":"hello staging"}'
```

## Notes pédagogiques

- Le frontend utilise `import.meta.env.VITE_API_URL`.
- En **staging/prod**, `VITE_API_URL` est injecté **au build** via `build.args` dans `compose.*.yml` et `ARG` dans `frontend/Dockerfile`.
- Le backend lit le secret depuis `/run/secrets/api_token_secret` (monté en read-only).
- Le reverse proxy Nginx route les requêtes `/api/*` vers le backend et le reste vers le frontend.

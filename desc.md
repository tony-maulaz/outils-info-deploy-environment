Génère un projet d’exemple pédagogique “FastAPI + Vue + SQLite” focalisé sur la gestion d’environnements Docker Compose (dev/staging/prod).

OBJECTIF PÉDAGOGIQUE
- Montrer une architecture minimale avec 1 fichier backend + 1 fichier frontend, et surtout la gestion de configuration:
  - Variables d’environnement non sensibles via .env (database_url, log_level, app_env, ports, domains…)
  - Secrets séparés (token secret, etc.) via fichiers montés (./secrets/...) ou docker secrets-like pattern.
- Pouvoir lancer dev, staging, prod sur UNE SEULE machine sans collisions (containers, réseaux, volumes, ports).
- Utiliser des ports différents pour staging et prod (pas de reverse proxy).
- Produire des fichiers .env.example clairs pour chaque environnement.

STACK TECHNIQUE
- Backend: FastAPI + Uvicorn, SQLite, 1 seul fichier Python (ex: backend/main.py)
  - il faut utiliser uv pour gèrer les dépendance et le lancement
- Frontend: Vue 3, 1 seul composant monofichier (ex: frontend/src/App.vue) + un main minimal
- Docker: docker-compose avec base + overrides

CONTRAINTES IMPORTANTES
- Backend “hyper simple”: endpoints:
  - GET /api/health -> {status:"ok", env:"...", db:"ok"}
  - GET /api/items -> liste en mémoire + ou table SQLite très simple (id, name)
  - POST /api/items -> ajoute un item
- SQLite: fichier dans un volume docker dédié à chaque env (staging/prod séparés).
- Le backend lit DATABASE_URL depuis env (ex: sqlite:///data/app.db).
- Secrets:
  - Un secret “API_TOKEN_SECRET” (ou JWT_SECRET) doit être lu depuis un fichier monté (ex: /run/secrets/api_token_secret)
  - Simuler un mot de passe DB dans un fichier monté (ex: /run/secrets/db_password)
  - Prévoir un répertoire local ./secrets (non versionné) + exemples ./secrets.example (versionné)
- Frontend:
  - Doit utiliser VITE_API_URL pour appeler l’API.
  - EXIGENCE: VITE_API_URL doit être passé au build via “args” dans l’image Docker (build args), pas seulement runtime.
  - Le frontend affiche:
    - un titre, l’environnement, le résultat /api/health
    - une mini liste d’items + un champ pour ajouter un item (appel POST)
- CORS: backend autorise l’origine du frontend (configurable par env).
- Dev local:
  - possibilité de lancer backend en reload (uvicorn --reload)
  - frontend en dev server (Vite) exposé sur un port (ex: 5173)
- Staging/Prod:
  - frontend buildé et servi via Nginx (conteneur frontend), sans reverse proxy.
  - backend en mode production (pas reload).

STRUCTURE DE DOSSIERS À GÉNÉRER
- backend/
  - main.py (unique fichier)
  - Dockerfile
  - requirements.txt (ou pyproject, mais simple)
- frontend/
  - src/App.vue (monofichier)
  - src/main.js (minimal)
  - index.html
  - package.json
  - vite.config.js
  - Dockerfile (avec build args VITE_API_URL)
- compose.yml (base)
- compose.dev.yml
- compose.staging.yml
- compose.prod.yml
- .env.dev.example
- .env.staging.example
- .env.prod.example
- .gitignore (doit ignorer .env, secrets/, data/, etc.)
- README.md clair, orienté “cours”, expliquant:
  - Différence entre variables non sensibles (.env) et secrets (fichiers)
  - Comment lancer chaque environnement
  - Comment lancer staging + prod simultanément sur la même machine
  - Comment tester via curl et via navigateur

EXIGENCES DOCKER COMPOSE (IMPORTANT)
- Utiliser “COMPOSE_PROJECT_NAME” ou “name:” pour isoler staging vs prod (deux stacks séparées).
- Les services doivent être nommés par env quand nécessaire (backend_staging, backend_prod…).
- Ports:
  - Dev: backend sur 8000, frontend sur 5173 (exposés)
  - Staging + prod: exposer les ports frontend + backend sur l’hôte avec des valeurs différentes
- Volumes:
  - data_staging, data_prod distincts (SQLite)
- Secrets:
  - monter ./secrets/<env>/api_token_secret.txt vers /run/secrets/api_token_secret (read-only)
  - fournir un dossier ./secrets.example/<env>/api_token_secret.txt (valeur dummy) + instructions copie
  - monter ./secrets/<env>/db_password.txt vers /run/secrets/db_password (read-only)
  - fournir un dossier ./secrets.example/<env>/db_password.txt (valeur dummy) + instructions copie

CONFIG ENVIRONNEMENTS
- Variables non sensibles typiques dans .env.*:
  - APP_ENV=dev|staging|prod
  - DATABASE_URL=sqlite:////data/app.db
  - LOG_LEVEL=debug|info
  - BACKEND_PORT=8000 (dev)
  - FRONTEND_PORT=5173 (dev)
  - VITE_API_URL=http://localhost:8000 (dev) / http://localhost:8001 (staging) / http://localhost:8002 (prod)
  - CORS_ORIGINS=...
- Secrets (fichiers):
  - API_TOKEN_SECRET (utilisé dans backend pour signer/vérifier un JWT, au minimum)
  - DB_PASSWORD (simulé pour l’exemple, même si SQLite n’en a pas besoin)

NIVEAU DE COMPLEXITÉ
- Très simple, didactique, aucun superflu.
- Code commenté pour étudiants.
- Tout doit fonctionner avec “docker compose”.

COMMANDES À DOCUMENTER DANS README
- Dev:
  - docker compose --env-file .env.dev -f compose.yml -f compose.dev.yml up --build
- Staging:
  - docker compose --env-file .env.staging -f compose.yml -f compose.staging.yml up -d --build
- Prod:
  - docker compose --env-file .env.prod -f compose.yml -f compose.prod.yml up -d --build
- Staging + Prod ensemble (sur même machine):
  - montrer comment lancer les deux avec des project names distincts:
    - COMPOSE_PROJECT_NAME=myapp_staging docker compose ...
    - COMPOSE_PROJECT_NAME=myapp_prod docker compose ...
  - ports distincts pour éviter les collisions

LIVRABLE FINAL
- Génère tous les fichiers.
- Assure-toi que le projet démarre sans modification autre que copier les .env.example en .env.* et copier secrets.example -> secrets.
- Ajoute des exemples de requêtes curl.

NOTE SUR VITE_API_URL (OBLIGATOIRE)
- Le Dockerfile du frontend doit accepter ARG VITE_API_URL, l’exposer à Vite au build (ENV VITE_API_URL=...), et le code Vue doit utiliser import.meta.env.VITE_API_URL.
- Dans docker-compose, passer build.args.VITE_API_URL depuis le .env de l’environnement.

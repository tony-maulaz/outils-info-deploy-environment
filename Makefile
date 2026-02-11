.PHONY: dev-up dev-down dev-logs staging-up staging-down staging-logs prod-up prod-down prod-logs

# Dev

dev-up:
	docker compose --env-file .env.dev -f compose.yml -f compose.dev.yml up --build

dev-down:
	docker compose --env-file .env.dev -f compose.yml -f compose.dev.yml down

dev-logs:
	docker compose --env-file .env.dev -f compose.yml -f compose.dev.yml logs -f --tail=100

# Staging

staging-up:
	docker compose --env-file .env.staging -f compose.yml -f compose.staging.yml up -d --build

staging-down:
	docker compose --env-file .env.staging -f compose.yml -f compose.staging.yml down

staging-logs:
	docker compose --env-file .env.staging -f compose.yml -f compose.staging.yml logs -f --tail=100

# Prod

prod-up:
	docker compose --env-file .env.prod -f compose.yml -f compose.prod.yml up -d --build

prod-down:
	docker compose --env-file .env.prod -f compose.yml -f compose.prod.yml down

prod-logs:
	docker compose --env-file .env.prod -f compose.yml -f compose.prod.yml logs -f --tail=100

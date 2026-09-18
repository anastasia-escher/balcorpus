
env_var:
export GIT_VERSION=$(git describe --always)
export GIT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
export GIT_LASTCOMMITDATE=$(git log -1 --format=%cI)
export GIT_COMMITHASH=$(git rev-parse HEAD)


redeploy: env_var
	@git pull
	@docker compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d --force-recreate
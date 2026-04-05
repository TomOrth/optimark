# Local Development Stack

This document defines the local infrastructure used for Optimark development in issue `#2`.

## Services
The local stack uses:
- Postgres for relational persistence
- Redis for background work coordination
- SeaweedFS for S3-compatible object storage

SeaweedFS is used in place of MinIO for local S3-compatible development.

## Prerequisites
- Docker
- Docker Compose

## Environment defaults
Copy the example environment file if you want to customize local ports or credentials:

```sh
cp .env.example .env
```

If `.env` is not present, the compose stack uses the defaults in `compose.yaml`.

## Start the stack
```sh
make dev-services-up
```

This starts:
- Postgres on `localhost:5432`
- Redis on `localhost:6379`
- SeaweedFS master UI on `localhost:9333`
- SeaweedFS filer UI on `localhost:8888`
- SeaweedFS S3 endpoint on `localhost:8333`

## Stop the stack
```sh
make dev-services-down
```

## Reset the stack
This removes local development volumes and clears persisted data.

```sh
make dev-services-reset
```

## Tail logs
```sh
make dev-services-logs
```

## Connection defaults
### Postgres
- Host: `localhost`
- Port: `5432`
- Database: `optimark`
- User: `optimark`
- Password: `optimark`

### Redis
- URL: `redis://localhost:6379/0`

### SeaweedFS S3
- Endpoint: `http://localhost:8333`
- Access key: `admin`
- Secret key: `key`
- Region: `us-east-1`
- Default development bucket name: `optimark-dev`

### Backend-oriented environment variables
The root `.env.example` includes application-facing defaults for future backend wiring:
- `BACKEND_DATABASE_URL`
- `BACKEND_REDIS_URL`
- `BACKEND_S3_ENDPOINT_URL`
- `BACKEND_S3_REGION`
- `BACKEND_S3_BUCKET`
- `BACKEND_S3_ACCESS_KEY_ID`
- `BACKEND_S3_SECRET_ACCESS_KEY`

## Notes
- This stack is for local development only.
- No cloud provisioning or production deployment concerns are included here.
- SeaweedFS is started in a single-node mode appropriate for development and testing.

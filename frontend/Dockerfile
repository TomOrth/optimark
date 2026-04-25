# syntax=docker/dockerfile:1

FROM dhi.io/bun:1 AS build

WORKDIR /app/frontend

COPY --chown=65532:65532 frontend/ ./

RUN ["bun", "install", "--frozen-lockfile"]

WORKDIR /app/frontend/packages/calliope
RUN ["bun", "x", "tsc", "-p", "tsconfig.json"]

WORKDIR /app/frontend/apps/apollo
RUN ["bun", "x", "tsc", "--noEmit"]
RUN ["bun", "x", "vite", "build"]

FROM dhi.io/bun:1 AS runtime

WORKDIR /app

ENV HOST=0.0.0.0
ENV PORT=4173

COPY --chown=65532:65532 --from=build /app/frontend/apps/apollo/dist ./dist
COPY --chown=65532:65532 frontend/apps/apollo/server.ts ./server.ts

EXPOSE 4173

CMD ["bun", "run", "server.ts"]

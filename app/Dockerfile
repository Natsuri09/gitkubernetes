# =============================================================================
# File    : app/Dockerfile
# Purpose : One Dockerfile, three images. Behaviour is chosen with build args.
# Build   : docker build --build-arg APP_VERSION=1.0.0 \
#                 -t notice-board:02230137-1.0.0 app/
#           (full commands for all three tags are in README.md)
# =============================================================================
# Alpine-based, as the rules require. Pinned to a minor series so rebuilds match.
FROM python:3.13-alpine

# Build arguments; the defaults give the 1.0.0 baseline.
ARG APP_VERSION=1.0.0
ARG BROKEN=false
ARG STUDENT_ID=02230137

# Baked into the image so /version needs no run-time configuration.
ENV APP_VERSION=${APP_VERSION} \
    BROKEN=${BROKEN} \
    STUDENT_ID=${STUDENT_ID} \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Non-root user with a NUMERIC uid, so Kubernetes can verify runAsNonRoot.
RUN addgroup -S -g 10001 app && adduser -S -u 10001 -G app app

WORKDIR /app
COPY app.py .

USER 10001
EXPOSE 8080
ENTRYPOINT ["python", "/app/app.py"]

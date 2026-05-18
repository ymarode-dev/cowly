#!/usr/bin/env bash
# Build all Cowly service images with the version from VERSION (or COWLY_VERSION).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

VERSION="${COWLY_VERSION:-$(tr -d '[:space:]' < VERSION)}"
REGISTRY="${COWLY_IMAGE_REGISTRY:-cowly}"
BUILD_TIMESTAMP="${COWLY_BUILD_TIMESTAMP:-$(date -u +%Y-%m-%dT%H:%M:%SZ)}"
VCS_REF="${COWLY_VCS_REF:-$(git rev-parse --short HEAD 2>/dev/null || echo unknown)}"
PUSH="${PUSH:-false}"

SERVICES=(
  api-gateway
  auth-service
  herd-service
  collar-registry
  collar-simulator
  telemetry-service
  alert-service
  notification-service
  seed-service
)

BUILD_ARGS=(
  --build-arg "COWLY_VERSION=${VERSION}"
  --build-arg "BUILD_TIMESTAMP=${BUILD_TIMESTAMP}"
  --build-arg "VCS_REF=${VCS_REF}"
)

echo "==> Building Cowly ${VERSION} (registry: ${REGISTRY})"

for svc in "${SERVICES[@]}"; do
  image="${REGISTRY}/${svc}:${VERSION}"
  context="${ROOT}/${svc}"
  echo ""
  echo "==> ${image}"
  docker build "${BUILD_ARGS[@]}" -t "${image}" "${context}"
  if [[ "${PUSH}" == "true" ]]; then
    docker push "${image}"
  fi
  # Also tag as latest for convenience
  docker tag "${image}" "${REGISTRY}/${svc}:latest"
  if [[ "${PUSH}" == "true" ]]; then
    docker push "${REGISTRY}/${svc}:latest"
  fi
done

echo ""
echo "Built ${#SERVICES[@]} images tagged ${REGISTRY}/*:${VERSION}"
if [[ "${PUSH}" != "true" ]]; then
  echo "Push to registry: PUSH=true ./scripts/build-and-push.sh"
fi
echo "Run pulled stack:  COWLY_VERSION=${VERSION} docker compose -f docker-compose.pull.yml up -d"

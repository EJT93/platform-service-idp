#!/usr/bin/env bash
set -euo pipefail

# Package Lambda function and optionally upload to S3
# Usage:
#   ./scripts/package-lambda.sh                          # package only
#   ./scripts/package-lambda.sh --upload <bucket> <key>  # package + upload

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="${SCRIPT_DIR}/../app"
BUILD_DIR="${APP_DIR}/build"
ZIP_PATH="${APP_DIR}/lambda.zip"

echo "==> Cleaning previous build..."
rm -rf "${BUILD_DIR}" "${ZIP_PATH}"
mkdir -p "${BUILD_DIR}"

echo "==> Installing dependencies..."
pip install -r "${APP_DIR}/requirements.txt" -t "${BUILD_DIR}" --quiet

echo "==> Copying source code..."
cp -r "${APP_DIR}/src/"* "${BUILD_DIR}/"

echo "==> Creating zip package..."
(cd "${BUILD_DIR}" && zip -r "${ZIP_PATH}" . -q)

echo "==> Package created: ${ZIP_PATH}"
echo "    Size: $(du -h "${ZIP_PATH}" | cut -f1)"

# Upload to S3 if --upload flag is provided
if [[ "${1:-}" == "--upload" ]]; then
  BUCKET="${2:?Usage: $0 --upload <bucket> <s3-key>}"
  S3_KEY="${3:?Usage: $0 --upload <bucket> <s3-key>}"
  echo "==> Uploading to s3://${BUCKET}/${S3_KEY}..."
  aws s3 cp "${ZIP_PATH}" "s3://${BUCKET}/${S3_KEY}"
  echo "==> Upload complete."
fi

# Cleanup build dir
rm -rf "${BUILD_DIR}"

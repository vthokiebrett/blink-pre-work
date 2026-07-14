#!/usr/bin/env bash
# Build one brand's form, commit, push, and print its live URL.
# Usage: ./publish.sh <brand-slug>
set -euo pipefail

SLUG="${1:-}"
if [ -z "$SLUG" ]; then
  echo "Usage: ./publish.sh <brand-slug>"
  echo "Brand files available:"
  ls brands/*.json 2>/dev/null | sed 's#brands/##; s#\.json##' | sed 's/^/  /'
  exit 1
fi

BRAND="brands/${SLUG}.json"
if [ ! -f "$BRAND" ]; then
  echo "No brand file: $BRAND"
  exit 1
fi

python3 build.py "$BRAND"

git add -A
if git diff --cached --quiet; then
  echo "Nothing to commit (no changes)."
else
  git commit -m "Publish ${SLUG} discovery pre-work"
  git push
fi

USER="$(git config --get remote.origin.url | sed -E 's#.*[:/]([^/]+)/[^/]+$#\1#')"
echo ""
echo "Live URL: https://${USER}.github.io/blink-pre-work/${SLUG}/"

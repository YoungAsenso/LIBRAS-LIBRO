#!/usr/bin/env bash
set -e
gunicorn -w 1 -b 0.0.0.0:${PORT:-8080} app:app
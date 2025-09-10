#!/usr/bin/env bash
set -eux

git checkout dev
git fetch -f origin main:main
git fetch -f origin rc:rc
git fetch -f origin testing:testing
git fetch -f origin daily:daily
git pull origin dev

#!/usr/bin/env bash
set -eux

git checkout dev
git fetch -fp origin

git update-ref -m sync --stdin <<EOF
start
update refs/heads/main origin/main
update refs/heads/rc origin/rc
update refs/heads/testing origin/testing
update refs/heads/daily origin/daily
prepare
commit
EOF

git rebase origin/dev dev

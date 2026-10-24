#!/bin/sh
# Replace SESSION_ID with the confirmed session ID before saving this template.
set -eu
cd -- "$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
exec opencode -s 'SESSION_ID'

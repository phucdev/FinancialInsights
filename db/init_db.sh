#!/usr/bin/env bash
set -euo pipefail
# Feed commands in schema.sql to the MySQL client
mysql -h mysql -u root -p"${MYSQL_ROOT_PASSWORD}" < /docker-entrypoint-initdb.d/schema.sql
echo "Schema applied."

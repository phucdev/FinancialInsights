#!/usr/bin/env bash
set -euo pipefail

BROKER="${KAFKA_BROKER:-broker:29092}"
IFS=',' read -ra TOPICS <<< "${KAFKA_TOPICS}"

for t in "${TOPICS[@]}"; do
  NAME=$(echo "$t" | cut -d: -f1)
  PARTS=$(echo "$t" | cut -d: -f2)
  REPL=$(echo "$t" | cut -d: -f3)
  echo "Creating topic $NAME (partitions=$PARTS, rf=$REPL) on $BROKER"
  /opt/kafka/bin/kafka-topics.sh \
    --bootstrap-server "$BROKER" \
    --create --if-not-exists \
    --topic "$NAME" \
    --partitions "$PARTS" \
    --replication-factor "$REPL"
done

echo "Topics created."

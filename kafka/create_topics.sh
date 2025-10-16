#!/usr/bin/env bash
set -euo pipefail

BROKER="${KAFKA_BROKER:-broker:29092}"  # Default broker address is 'broker:29092'
IFS=',' read -ra TOPICS <<< "${KAFKA_TOPICS}"  # Read topics from environment variable, separated by commas

for t in "${TOPICS[@]}"; do
  NAME=$(echo "$t" | cut -d: -f1)  # Topic name is the first part, cut by ':'
  PARTS=$(echo "$t" | cut -d: -f2)
  REPL=$(echo "$t" | cut -d: -f3)
  echo "Creating topic $NAME (partitions=$PARTS, rf=$REPL) on $BROKER"
  /usr/bin/kafka-topics \
    --bootstrap-server "$BROKER" \
    --create --if-not-exists \
    --topic "$NAME" \
    --partitions "$PARTS" \
    --replication-factor "$REPL"
done

echo "Topics created."

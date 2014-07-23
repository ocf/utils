#!/bin/bash
HOST="$1"
IP="$2"

./tmpl.sh "$HOST" "$IP" | ldapadd

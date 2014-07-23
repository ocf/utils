#!/bin/bash
HOST="$1"
IP="$2"

echo "dn: cn=$HOST,ou=Hosts,dc=OCF,dc=Berkeley,dc=EDU"
echo "objectClass: device"
echo "objectClass: ocfDevice"
echo "cn: $HOST"
echo "ipHostNumber: $IP"
echo "type: server"
echo "environment: production"

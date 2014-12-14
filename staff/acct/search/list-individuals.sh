#!/bin/bash
# Prints a list of unsorried individual accounts.

ldapsearch -xb 'ou=People,dc=OCF,dc=Berkeley,dc=EDU' \
	'(&(!(|(callinkOid=*)(oslGid=*)))(!(gidNumber=2390)))' \
	| grep '^uid:' | cut -d' ' -f2

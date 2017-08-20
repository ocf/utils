#!/bin/bash

which shellcheck &> /dev/null
if [[ $? != 0 ]]; then
    echo "are you sure you have installed shellcheck?"
    exit 1
fi

shellcheck "$@"
exit $?

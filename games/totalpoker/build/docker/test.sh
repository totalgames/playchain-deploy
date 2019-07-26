#!/bin/bash

CONFIG_DEBUG=$1

if [[ -n "${CONFIG_DEBUG}" && ${CONFIG_DEBUG} = ON ]]; then
    echo ">> CONFIG_DEBUG = ON"
else
    echo ">> CONFIG_DEBUG = OFF"
fi
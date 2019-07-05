#!/bin/bash

if [ $CONFIG_DEBUG = ON ]; then
    echo ">> * ROOMENTRY.SH"
    echo '>> HOME = '$HOME
    echo '>> USER = '$USER
    echo '>> CONFIGURATE = '$CONFIGURATE
    echo '>> CONFIG_OFF_LOGO = '$CONFIG_OFF_LOGO
    echo '>> CONFIG_DEBUG = '$CONFIG_DEBUG
    echo '>> CONFIG_EXTERNAL_PLAYCHAIN_DATABASE_API_URL = '$CONFIG_EXTERNAL_PLAYCHAIN_DATABASE_API_URL
    echo '>> CONFIG_EXTERNAL_PLAYCHAIN_DATABASE_P2P_URL = '$CONFIG_EXTERNAL_PLAYCHAIN_DATABASE_P2P_URL
    echo '>> CONFIG_PLAYCHAIN_DATABASE_API_PORT = '$CONFIG_PLAYCHAIN_DATABASE_API_PORT
    echo '>> CONFIG_PLAYCHAIN_DATABASE_TLS_API_PORT = '$CONFIG_PLAYCHAIN_DATABASE_TLS_API_PORT
    echo '>> CONFIG_PLAYCHAIN_DATABASE_P2P_PORT = '$CONFIG_PLAYCHAIN_DATABASE_P2P_PORT
    echo '>> CONFIG_POKER_ROOM_PORT = '$CONFIG_POKER_ROOM_PORT
    echo '>> CONFIG_POKER_ROOM_CONTROL_PORT = '$CONFIG_POKER_ROOM_CONTROL_PORT
    echo '>> CONFIG_TEST_TAG = '$CONFIG_TEST_TAG
    echo '>> CONFIG_GENESIS = '$CONFIG_GENESIS
fi

ENV_EXPORT_DIR=${HOME}/.environment
mkdir -p ${ENV_EXPORT_DIR} || exit 1
cd ${ENV_EXPORT_DIR}
echo $CONFIG_OFF_LOGO > "CONFIG_OFF_LOGO"
echo $CONFIG_DEBUG > "CONFIG_DEBUG"
echo $CONFIG_EXTERNAL_PLAYCHAIN_DATABASE_API_URL > "CONFIG_EXTERNAL_PLAYCHAIN_DATABASE_API_URL"
echo $CONFIG_EXTERNAL_PLAYCHAIN_DATABASE_P2P_URL > "CONFIG_EXTERNAL_PLAYCHAIN_DATABASE_P2P_URL"
echo $CONFIG_PLAYCHAIN_DATABASE_API_PORT > "CONFIG_PLAYCHAIN_DATABASE_API_PORT"
echo $CONFIG_PLAYCHAIN_DATABASE_TLS_API_PORT > "CONFIG_PLAYCHAIN_DATABASE_TLS_API_PORT"
echo $CONFIG_PLAYCHAIN_DATABASE_P2P_PORT > "CONFIG_PLAYCHAIN_DATABASE_P2P_PORT"
echo $CONFIG_POKER_ROOM_PORT > "CONFIG_POKER_ROOM_PORT"
echo $CONFIG_POKER_ROOM_CONTROL_PORT > "CONFIG_POKER_ROOM_CONTROL_PORT"
echo $CONFIG_TEST_TAG > "CONFIG_TEST_TAG"
echo $CONFIG_GENESIS > "CONFIG_GENESIS"

if [ -n "$CONFIG_TEST_TAG" ]; then
    cp /etc/room/tables.${CONFIG_TEST_TAG}.info "${HOME}/tables.info" || exit 1
else
    if [ $LIVE_TESTNET = ON ]; then
        cp /etc/room/tables.stage.info "${HOME}/tables.info" || exit 1
    else
        cp /etc/room/tables.prod.info "${HOME}/tables.info" || exit 1
    fi
fi

PYTHON_BIN=$(which python3)
ROOMENTRY_BIN="/usr/local/bin/roomentry.py"

ulimit -c unlimited

exec chpst -u ${USER} -e ${ENV_EXPORT_DIR} ${PYTHON_BIN} ${ROOMENTRY_BIN}

#!/bin/bash

if [ -d $(dirname ${BASH_SOURCE}) ]; then
    cd $(dirname ${BASH_SOURCE})
fi

if [ $# -le 1 ]; then
    SELF_NAME=`basename "$0"`
    echo "Invalid incoming parameters count!"
    echo "Usage:"
    echo "    ${SELF_NAME} branch (for playchain) configuration (path to your config)"
    exit 1
fi

source ../playchain.lib.sh

BRANCH_NAME_PLAYCHAIN="$1"
load_config $2 CONFIG_FILE

echo "***************************************************************************"
echo "Installing branch '$BRANCH_NAME_PLAYCHAIN' for playchain" 
echo "with configuration file $CONFIG_FILE"
echo "***************************************************************************"

echo "CONFIG IS:"
echo "DOCKER_IMAGE_NAME is $DOCKER_IMAGE_NAME"
echo "CONFIG_OFF_LOGO is $CONFIG_OFF_LOGO"
echo "CONFIG_DEBUG is $CONFIG_DEBUG"
echo "CONFIG_EXTERNAL_PLAYCHAIN_DATABASE_API_URL is $CONFIG_EXTERNAL_PLAYCHAIN_DATABASE_API_URL"
echo "CONFIG_EXTERNAL_PLAYCHAIN_DATABASE_P2P_URL is $CONFIG_EXTERNAL_PLAYCHAIN_DATABASE_P2P_URL"
echo "CONFIG_PLAYCHAIN_DATABASE_API_INTERFACE is $CONFIG_PLAYCHAIN_DATABASE_API_INTERFACE"
echo "CONFIG_PLAYCHAIN_DATABASE_API_PORT is $CONFIG_PLAYCHAIN_DATABASE_API_PORT"
echo "CONFIG_PLAYCHAIN_DATABASE_P2P_INTERFACE is $CONFIG_PLAYCHAIN_DATABASE_P2P_INTERFACE"
echo "CONFIG_PLAYCHAIN_DATABASE_P2P_PORT is $CONFIG_PLAYCHAIN_DATABASE_P2P_PORT"

pushd build

get_temp_dir TEMP_DIR
get_build_dir BUILD_DIR
clone_repository https://github.com/totalgames/playchain-core.git $BRANCH_NAME_PLAYCHAIN playchain SRC_DIR_FOR_PLAYCHAN
SRC_DIR_FOR_PLAYCHAN=_git/playchain

echo "TEMP_DIR is $TEMP_DIR"
echo "BUILD_DIR is $BUILD_DIR"
echo "SRC_DIR_FOR_PLAYCHAN is $SRC_DIR_FOR_PLAYCHAN"
echo "PWD is $PWD"

echo "* Docker image creating"
if [[ $CONFIG_FILE =~ testnet.*$ ]]; then
    docker build -t ${DOCKER_IMAGE_NAME} \
    --build-arg PLAYCHAIN_SRC_DIR=${SRC_DIR_FOR_PLAYCHAN} \
    --build-arg LIVE_TESTNET=ON \
    -f Dockerfile  .
else
    docker build -t ${DOCKER_IMAGE_NAME} \
    --build-arg PLAYCHAIN_SRC_DIR=${SRC_DIR_FOR_PLAYCHAN} \
    -f Dockerfile .
fi

if [ $? -ne 0 ]; then
    echo "BUILD ERROR"
    exit 1
fi

PAYLOAD_DIR=${TEMP_DIR}/_payload
rm -rf ${PAYLOAD_DIR}
mkdir ${PAYLOAD_DIR}
WITNESS_DOCKER_IMAGE_TAR=${PAYLOAD_DIR}/${DOCKER_IMAGE_NAME}
echo "* Docker image file saving"
docker save -o ${WITNESS_DOCKER_IMAGE_TAR} ${DOCKER_IMAGE_NAME}
chmod 644 ${WITNESS_DOCKER_IMAGE_TAR}

echo "* Docker image file checksum calculation"
CHECK_SUM=$(sha256sum ${WITNESS_DOCKER_IMAGE_TAR} |cut -d ' ' -f 1)

echo "CHECK_SUM is $CHECK_SUM"

cat docker/installer.sh \
    | sed s+'${_WITNESS_DOCKER_IMAGE_NAME}'+${DOCKER_IMAGE_NAME}+ \
    | sed s+'${_CONFIG_OFF_LOGO}'+${CONFIG_OFF_LOGO}+ \
    | sed s+'${_CONFIG_DEBUG}'+${CONFIG_DEBUG}+ \
    | sed s+'${_CONFIG_EXTERNAL_PLAYCHAIN_DATABASE_API_URL}'+${CONFIG_EXTERNAL_PLAYCHAIN_DATABASE_API_URL}+ \
    | sed s+'${_CONFIG_EXTERNAL_PLAYCHAIN_DATABASE_P2P_URL}'+${CONFIG_EXTERNAL_PLAYCHAIN_DATABASE_P2P_URL}+ \
    | sed s+'${_CONFIG_PLAYCHAIN_DATABASE_API_INTERFACE}'+${CONFIG_PLAYCHAIN_DATABASE_API_INTERFACE}+ \
    | sed s+'${_CONFIG_PLAYCHAIN_DATABASE_API_PORT}'+${CONFIG_PLAYCHAIN_DATABASE_API_PORT}+ \
    | sed s+'${_CONFIG_PLAYCHAIN_DATABASE_P2P_INTERFACE}'+${CONFIG_PLAYCHAIN_DATABASE_P2P_INTERFACE}+ \
    | sed s+'${_CONFIG_PLAYCHAIN_DATABASE_P2P_PORT}'+${CONFIG_PLAYCHAIN_DATABASE_P2P_PORT}+ \
    | sed s+'${_CHECK_SUM}'+${CHECK_SUM}+ \
    > ${PAYLOAD_DIR}/installer.sh
chmod +x ${PAYLOAD_DIR}/installer.sh
cp docker/decompress.sh ${TEMP_DIR}/decompress

pushd ${PAYLOAD_DIR}

ARCH_NAME=${DOCKER_IMAGE_NAME}.tar.gz
echo "* Docker image file archivation"
tar czf ${BUILD_DIR}/${ARCH_NAME} ./*
pushd ${BUILD_DIR}

if [ -e "${ARCH_NAME}" ]; then
    echo "* BSX creation"
    cat ${TEMP_DIR}/decompress ${ARCH_NAME} > ${DOCKER_IMAGE_NAME}.bsx
    rm -f ${ARCH_NAME}
else
    echo "${ARCH_NAME} does not exist"
    exit 1
fi

chmod a+x ${DOCKER_IMAGE_NAME}.bsx

popd #${BUILD_DIR}
popd #${PAYLOAD_DIR}
popd #build

echo "${DOCKER_IMAGE_NAME}.bsx created"

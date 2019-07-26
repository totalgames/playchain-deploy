#!/bin/bash

DOCKER_IMAGE_NAME=${_WITNESS_DOCKER_IMAGE_NAME}
CONFIG_OFF_LOGO=${_CONFIG_OFF_LOGO}
CONFIG_DEBUG=${_CONFIG_DEBUG}
CONFIG_EXTERNAL_PLAYCHAIN_DATABASE_API_URL=${_CONFIG_EXTERNAL_PLAYCHAIN_DATABASE_API_URL}
CONFIG_EXTERNAL_PLAYCHAIN_DATABASE_P2P_URL=${_CONFIG_EXTERNAL_PLAYCHAIN_DATABASE_P2P_URL}
CONFIG_PLAYCHAIN_DATABASE_API_INTERFACE=${_CONFIG_PLAYCHAIN_DATABASE_API_INTERFACE}
CONFIG_PLAYCHAIN_DATABASE_API_PORT=${_CONFIG_PLAYCHAIN_DATABASE_API_PORT}
CONFIG_PLAYCHAIN_DATABASE_TLS_API_INTERFACE=${_CONFIG_PLAYCHAIN_DATABASE_TLS_API_INTERFACE}
CONFIG_PLAYCHAIN_DATABASE_TLS_API_PORT=${_CONFIG_PLAYCHAIN_DATABASE_TLS_API_PORT}
CONFIG_PLAYCHAIN_DATABASE_P2P_INTERFACE=${_CONFIG_PLAYCHAIN_DATABASE_P2P_INTERFACE}
CONFIG_PLAYCHAIN_DATABASE_P2P_PORT=${_CONFIG_PLAYCHAIN_DATABASE_P2P_PORT}
CONFIG_POKER_ROOM_INTERFACE=${_CONFIG_POKER_ROOM_INTERFACE}
CONFIG_POKER_ROOM_PORT=${_CONFIG_POKER_ROOM_PORT}
CONFIG_POKER_ROOM_CONTROL_PORT=${_CONFIG_POKER_ROOM_CONTROL_PORT}
CONFIG_TEST_TAG=${_CONFIG_TEST_TAG}
CHECK_SUM=${_CHECK_SUM}

init_sudo()
{
    if [[ $EUID -ne 0 ]]; then
        SUDO="sudo"
        LOGIN=${USER}
        UNSUDO=""
    else
        SUDO=""
        LOGIN=$(who | awk '{print $1; exit}')
        UNSUDO="sudo -u ${LOGIN}"
    fi
    USER_HOME=$( getent passwd "$LOGIN" | cut -d: -f6 )
}

echo_debug()
{
    if [[ -n "${CONFIG_DEBUG}" && ${CONFIG_DEBUG} = ON ]]; then
        echo ">> $@"
    fi
}

echo_debug_env()
{
    if [[ -n "${CONFIG_DEBUG}" && ${CONFIG_DEBUG} = ON ]]; then
        echo ">> * INSTALLER.SH"
        echo ">> PLAYCHAIN_NODE_CONFIG_NOT_INTERACTIVE is $PLAYCHAIN_NODE_CONFIG_NOT_INTERACTIVE"
        echo ">> CONFIG_OFF_LOGO is $CONFIG_OFF_LOGO"
        echo ">> CONFIG_DEBUG is $CONFIG_DEBUG"
        echo ">> CONFIG_EXTERNAL_PLAYCHAIN_DATABASE_API_URL is $CONFIG_EXTERNAL_PLAYCHAIN_DATABASE_API_URL"
        echo ">> CONFIG_EXTERNAL_PLAYCHAIN_DATABASE_P2P_URL is $CONFIG_EXTERNAL_PLAYCHAIN_DATABASE_P2P_URL"
        echo ">> CONFIG_PLAYCHAIN_DATABASE_API_INTERFACE is $CONFIG_PLAYCHAIN_DATABASE_API_INTERFACE"
        echo ">> CONFIG_PLAYCHAIN_DATABASE_API_PORT is $CONFIG_PLAYCHAIN_DATABASE_API_PORT"
        echo ">> CONFIG_PLAYCHAIN_DATABASE_TLS_API_INTERFACE is $CONFIG_PLAYCHAIN_DATABASE_TLS_API_INTERFACE"
        echo ">> CONFIG_PLAYCHAIN_DATABASE_TLS_API_PORT is $CONFIG_PLAYCHAIN_DATABASE_TLS_API_PORT"
        echo ">> CONFIG_PLAYCHAIN_DATABASE_P2P_INTERFACE is $CONFIG_PLAYCHAIN_DATABASE_P2P_INTERFACE"
        echo ">> CONFIG_PLAYCHAIN_DATABASE_P2P_PORT is $CONFIG_PLAYCHAIN_DATABASE_P2P_PORT"
        echo ">> CONFIG_POKER_ROOM_INTERFACE is $CONFIG_POKER_ROOM_INTERFACE"
        echo ">> CONFIG_POKER_ROOM_PORT is $CONFIG_POKER_ROOM_PORT"
        echo ">> CONFIG_POKER_ROOM_CONTROL_PORT is $CONFIG_POKER_ROOM_CONTROL_PORT"
        echo ">> CONFIG_TEST_TAG is $CONFIG_TEST_TAG"
        echo ">> CHECK_SUM is $CHECK_SUM"
    fi
}

install_docker()
{
    echo_debug "install_docker"

    if test -t 2 && which docker >/dev/null 2>&1; then
        echo "* Docker is installed"
    else
        init_sudo

        echo "* Installing Docker repo"

        ${SUDO} apt-get install -y curl
        ${SUDO} apt-get install -y software-properties-common
        ${SUDO} apt-get install -y  apt-transport-https

        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | ${SUDO} apt-key add -

        _LINUX_DIST=$1
        if [  -z ${_LINUX_DIST} ]; then
            _LINUX_DIST=$(lsb_release -cs)
        else
            echo "* Using Linux '${_LINUX_DIST}'"
        fi

        ${SUDO} add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu ${_LINUX_DIST} stable"

        ${SUDO} apt-get update

        echo "* Installing docker"

        ${SUDO} apt-get install -y docker-ce

        ${SUDO} groupadd docker 2>/dev/null

        ${SUDO} gpasswd -a ${LOGIN} docker
    fi
}

install_node()
{
    echo_debug "install_node"

    local _WORK_DIR=$1

    if [[ ! -d ${_WORK_DIR} ]]; then
        echo "Work dir ${_WORK_DIR} is not found"
        exit 1
    fi

    cat > ${_WORK_DIR}/start.sh <<EOF
#!/bin/bash

if [[ \$EUID -ne 0 ]]; then
    SUDO="sudo"
else
    SUDO=""
fi
if [ -z \$(docker ps --format '{{.Names}}' 2>/dev/null|grep '^${DOCKER_IMAGE_NAME}.d\$') ]; then
    docker start ${DOCKER_IMAGE_NAME}.d
fi
EOF
    chmod ugo+x ${_WORK_DIR}/start.sh

    cat > ${_WORK_DIR}/stop.sh <<EOF
#!/bin/bash

if [[ \$EUID -ne 0 ]]; then
    SUDO="sudo"
else
    SUDO=""
fi
if [ -n "\$(docker ps --format '{{.Names}}' 2>/dev/null|grep '^${DOCKER_IMAGE_NAME}.d\$')" ]; then
    docker stop ${DOCKER_IMAGE_NAME}.d
fi
EOF
    chmod ugo+x ${_WORK_DIR}/stop.sh    
}

run_node()
{
    echo_debug "run_node"

    local _WORK_DIR=$1

    if [[ ! -d ${_WORK_DIR} ]]; then
        echo "Work dir ${_WORK_DIR} is not found"
        exit 1
    fi

    docker stop ${DOCKER_IMAGE_NAME} 2>/dev/null

    local _ARGS
    _ARGS="-p ${CONFIG_PLAYCHAIN_DATABASE_API_INTERFACE}:$CONFIG_PLAYCHAIN_DATABASE_API_PORT:$CONFIG_PLAYCHAIN_DATABASE_API_PORT"
    _ARGS="$_ARGS -p ${CONFIG_PLAYCHAIN_DATABASE_TLS_API_INTERFACE}:$CONFIG_PLAYCHAIN_DATABASE_TLS_API_PORT:$CONFIG_PLAYCHAIN_DATABASE_TLS_API_PORT"
    _ARGS="$_ARGS -p ${CONFIG_PLAYCHAIN_DATABASE_P2P_INTERFACE}:$CONFIG_PLAYCHAIN_DATABASE_P2P_PORT:$CONFIG_PLAYCHAIN_DATABASE_P2P_PORT"
    _ARGS="$_ARGS -p ${CONFIG_POKER_ROOM_INTERFACE}:$CONFIG_POKER_ROOM_PORT:$CONFIG_POKER_ROOM_PORT"
    _ARGS="$_ARGS -p ${CONFIG_POKER_ROOM_INTERFACE}:$CONFIG_POKER_ROOM_CONTROL_PORT:$CONFIG_POKER_ROOM_CONTROL_PORT"

    local _ENVS
    _ENVS="${_ENVS} -e CONFIG_EXTERNAL_PLAYCHAIN_DATABASE_API_URL=${CONFIG_EXTERNAL_PLAYCHAIN_DATABASE_API_URL}"
    _ENVS="${_ENVS} -e CONFIG_EXTERNAL_PLAYCHAIN_DATABASE_P2P_URL=${CONFIG_EXTERNAL_PLAYCHAIN_DATABASE_P2P_URL}"
    _ENVS="${_ENVS} -e CONFIG_PLAYCHAIN_DATABASE_API_PORT=${CONFIG_PLAYCHAIN_DATABASE_API_PORT}"
    _ENVS="${_ENVS} -e CONFIG_PLAYCHAIN_DATABASE_TLS_API_PORT=${CONFIG_PLAYCHAIN_DATABASE_TLS_API_PORT} "
    _ENVS="${_ENVS} -e CONFIG_PLAYCHAIN_DATABASE_P2P_PORT=${CONFIG_PLAYCHAIN_DATABASE_P2P_PORT}"
    _ENVS="${_ENVS} -e CONFIG_POKER_ROOM_PORT=${CONFIG_POKER_ROOM_PORT}"
    _ENVS="${_ENVS} -e CONFIG_POKER_ROOM_CONTROL_PORT=${CONFIG_POKER_ROOM_CONTROL_PORT}"
    if [ -f ${_WORK_DIR}/genesis.json ]; then
        _ENVS="${_ENVS} -e CONFIG_GENESIS=True"
    fi

    echo "* Run node"
    docker run --log-driver syslog -v ${_WORK_DIR}:/var/lib/room ${_ARGS} -d \
                ${_ENVS} \
                --name ${DOCKER_IMAGE_NAME}.d ${DOCKER_IMAGE_NAME}
    exit 0
}

function get_check_sum 
{
    echo_debug "get_check_sum"

    local _WORK_DIR=$1

    declare -n return_value=$2

    local VERSION_PATH=${_WORK_DIR}/version

	if [[ ! -f ${VERSION_PATH} ]]; then
		return_value=
    else
        return_value=$(cat ${VERSION_PATH})
	fi
}

function save_check_sum 
{
    echo_debug "save_check_sum"

    local _WORK_DIR=$1

    if [[ ! -d ${_WORK_DIR} ]]; then
        echo "Work dir ${_WORK_DIR} is not found"
        exit 1
    fi

    ${UNSUDO} mkdir -p ${_WORK_DIR}
    ${UNSUDO} echo $2 > ${_WORK_DIR}/version
}

main()
{
    local _WORK_ROOT_DIR
    if [ -n "$1" ]; then
        _WORK_ROOT_DIR=$1
    else
        echo "Config dir path is required"
        exit 1
    fi

    echo_debug_env
    echo_debug "CONFIG_WORK_DIR is $_WORK_ROOT_DIR"

    local _WORK_DIR=${_WORK_ROOT_DIR}/.data
    mkdir -p ${_WORK_DIR}
    if [ ! $? -eq 0  ]; then
        echo "Invalid config dir path ${_WORK_ROOT_DIR}"
        exit 1
    fi

    init_sudo
    install_docker

    local CURRENT_CHECK_SUM

    get_check_sum ${_WORK_DIR} CURRENT_CHECK_SUM

    if [[ $CURRENT_CHECK_SUM != $CHECK_SUM || \
     ! -e ${_WORK_DIR}/playchain.config.ini || \
     ! -e ${_WORK_DIR}/poker_room.config.ini ]]; then
        # ${SUDO} rm -rf ${_WORK_DIR}/blockchain
        docker stop ${DOCKER_IMAGE_NAME} 2>/dev/null
        docker rm ${DOCKER_IMAGE_NAME} 2>/dev/null
        docker rmi ${DOCKER_IMAGE_NAME} 2>/dev/null
        docker load -i ${DOCKER_IMAGE_NAME}
        ${UNSUDO} mkdir -p ${_WORK_DIR}
        local CONF_RESULT=0
        if [[ -z ${PLAYCHAIN_NODE_CONFIG_NOT_INTERACTIVE} ]]; then
            local _ARGS
            _ARGS="$_ARGS -p ${CONFIG_PLAYCHAIN_DATABASE_P2P_INTERFACE}:$CONFIG_PLAYCHAIN_DATABASE_P2P_PORT:$CONFIG_PLAYCHAIN_DATABASE_P2P_PORT"

            local _ENVS
            _ENVS="-e CONFIGURATE=True"
            _ENVS="${_ENVS} -e CONFIG_OFF_LOGO=${CONFIG_OFF_LOGO}"
            _ENVS="${_ENVS} -e CONFIG_DEBUG=${CONFIG_DEBUG}"
            _ENVS="${_ENVS} -e CONFIG_EXTERNAL_PLAYCHAIN_DATABASE_API_URL=${CONFIG_EXTERNAL_PLAYCHAIN_DATABASE_API_URL}"
            _ENVS="${_ENVS} -e CONFIG_EXTERNAL_PLAYCHAIN_DATABASE_P2P_URL=${CONFIG_EXTERNAL_PLAYCHAIN_DATABASE_P2P_URL}"
            _ENVS="${_ENVS} -e CONFIG_PLAYCHAIN_DATABASE_API_PORT=${CONFIG_PLAYCHAIN_DATABASE_API_PORT}"
            _ENVS="${_ENVS} -e CONFIG_PLAYCHAIN_DATABASE_TLS_API_PORT=${CONFIG_PLAYCHAIN_DATABASE_TLS_API_PORT} "
            _ENVS="${_ENVS} -e CONFIG_PLAYCHAIN_DATABASE_P2P_PORT=${CONFIG_PLAYCHAIN_DATABASE_P2P_PORT}"
            _ENVS="${_ENVS} -e CONFIG_POKER_ROOM_PORT=${CONFIG_POKER_ROOM_PORT}"
            _ENVS="${_ENVS} -e CONFIG_POKER_ROOM_CONTROL_PORT=${CONFIG_POKER_ROOM_CONTROL_PORT}"
            _ENVS="${_ENVS} -e CONFIG_TEST_TAG=${CONFIG_TEST_TAG}"
            if [ -f ${_WORK_DIR}/genesis.json ]; then
                _ENVS="${_ENVS} -e CONFIG_GENESIS=True"
            fi
            docker run -v ${_WORK_DIR}:/var/lib/room ${_ARGS} -it \
                ${_ENVS} \
                --rm --name ${DOCKER_IMAGE_NAME}.c ${DOCKER_IMAGE_NAME}
            CONF_RESULT=$?
            echo_debug "Result = $CONF_RESULT"
        fi
        if [[ $CONF_RESULT -eq 0 ]]; then
            if [ -n "${CHECK_SUM}" ]; then
                save_check_sum ${_WORK_DIR} ${CHECK_SUM}
            fi
            install_node ${_WORK_ROOT_DIR}
            docker rm ${DOCKER_IMAGE_NAME}.d 2>/dev/null
            run_node ${_WORK_DIR}
        else
            echo_debug "Error $CONF_RESULT"
            exit $CONF_RESULT
        fi
    else
        run_node ${_WORK_DIR}
    fi
}

main $@

#!/bin/bash

VERSION=0.0.2

SYSTEM=$(uname -s)

BLUE='\033[94m'
GREEN='\033[32;1m'
YELLOW='\033[33;1m'
RED='\033[91;1m'
RESET='\033[0m'

UNINSTALL=0

AVAILABLE_GAMES=("poker")
SETUP_GAME_FILE_ID=("1Uv5YHjzlc9Tm6tK-Z4pMHsZTKshKMy0K")
DEFAULT_GAME="poker"

SUDO=""

usage() {
    cat <<EOF

This is the install script for PlayChain game node.

Usage: $0 [-h] [-g <game>] [-t <target_directory>] [-u] [-i <path to setup image>]

-h
    Print usage.

-g <game>
    PlayChain game.
    Default: poker
    Availables: ${AVAILABLE_GAMES[*]}

-t <target_directory>
    Target directory for config files and binaries.
    Default: $HOME/.local/share/playchain_<game>

-u
    Uninstall PlayChain node.

-i
    Custom image file (if it is not set image will be downloaded from Google Drive)

EOF
}

print_info() {
    printf "$BLUE$1$RESET\n"
}

print_success() {
    printf "$GREEN$1$RESET\n"
    sleep 1
}

print_warning() {
    printf "$YELLOW$1$RESET\n"
}

print_error() {
    printf "$RED$1$RESET\n"
    sleep 1
}

print_debug() {
    # echo -n ""
    echo ">> " $@
}

program_exists() {
    type "$1" > /dev/null 2>&1
    return $?
}

create_target_dir() {
    if [ ! -d "${TARGET_DIR}" ]; then
        print_info "\nCreating target directory: ${TARGET_DIR}"
        mkdir -p ${TARGET_DIR}
    fi
    TARGET_DIR=$(realpath ${TARGET_DIR})
}

print_readme() {
    cat <<EOF

# README

To stop PlayChain:

    cd $TARGET_DIR && ./stop.sh

To start PlayChain again:

    cd $TARGET_DIR && ./start.sh

To view PlayChain log files:

    tail -f $TARGET_DIR/.data/logs/all.log
    tail -f $TARGET_DIR/.data/p2p/p2p.log
    # depends on game:
    tail -f /var/log/syslog

To uninstall PlayChain:

    ./node-deploy.sh -u

EOF
}

init_system_install() {
    if [ $(id -u) -ne 0 ]; then
        if program_exists "sudo"; then
            SUDO="sudo"
            print_info "\nInstalling required system packages.."
        else
            print_error "\nsudo program is required to install system packages. Please install sudo as root and rerun this script as normal user."
            exit 1
        fi
    fi
}

install_debian_build_dependencies() {
    $SUDO apt-get update
    $SUDO apt-get install -y \
        wget realpath
}

install_build_dependencies() {
    init_system_install
    case "$SYSTEM" in
        Linux)
            if program_exists "apt-get"; then
                install_debian_build_dependencies
            else
                print_error "\nSorry, your system is not supported by this installer."
                exit 1
            fi
            ;;
        # FreeBSD)
        #     install_freebsd_build_dependencies
        #     ;;
        *)
            print_error "\nSorry, your system is not supported by this installer."
            exit 1
            ;;
    esac
}

install_gdrive() {
    print_debug "install_gdrive"
    cd ${TARGET_DIR}
    wget -O ${TARGET_DIR}/gdrive --continue --progress=bar https://docs.google.com/uc?id=0B3X9GlR6EmbnWksyTEtCM0VfaFE&export=download
    wait
    print_debug "gdrive downloaded" 
    chmod ugo+x gdrive
}

download_node() {
    print_debug "download_node"

    install_gdrive
    print_debug "gdrive installed"  
    ./gdrive -c ${TARGET_DIR} list
    print_debug "downlod node setup image" 
    ./gdrive -c ${TARGET_DIR} download -f --stdout ${SETUP_GAME_FILE_ID[$1]} > ${TARGET_DIR}/setup.bsx
}

start_node() {
    print_debug "start_node"

    local RUN_IMAGE=${TARGET_DIR}/setup.bsx

    if [ -n "${1}" ]; then
        RUN_IMAGE=${1}
    fi

    if [ ! -f ${RUN_IMAGE} ]; then
        rint_error "Installation failed"
        exit 1
    fi

    RUN_IMAGE=$(realpath ${RUN_IMAGE})

    print_debug "start ${RUN_IMAGE}"

    chmod ugo+x ${RUN_IMAGE}
    ${RUN_IMAGE} ${TARGET_DIR}
    START_NODE_RESULT=$?
}

stop_node() {
    print_debug "stop_node"
    
    cd ${TARGET_DIR} && ./stop.sh
}

uninstall_node() {
    init_system_install
    stop_node

    if [ -d "${TARGET_DIR}" ]; then
        print_info "\nUninstalling PlayChain.."
        $SUDO rm -rf ${TARGET_DIR}

        if [ ! -d "${TARGET_DIR}" ]; then
            print_success "PlayChain uninstalled successfully!"
        else
            print_error "Uninstallation failed. Is PlayChain still running?"
            exit 1
        fi
    else
        print_error "PlayChain not installed."
    fi
}

GAME=${DEFAULT_GAME}
while getopts "hg:t:i:u" opt
do
    case "$opt" in
        g)
            print_debug "OPT = G: " ${OPTARG}
            GAME=${OPTARG}
            ;;
        t)
            print_debug "OPT = T: " ${OPTARG}
            TARGET_DIR=${OPTARG}
            ;;
        i)
            print_debug "OPT = T: " ${OPTARG}
            IMAGE_PATH=${OPTARG}
            ;;
        u)
            print_debug "OPT = U"
            UNINSTALL=1
            ;;
        h)
            print_debug "OPT = H"
            usage
            exit 0
            ;;
        ?)
            ;;
    esac
done

GAME=$(echo $GAME | tr [:upper:] [:lower:])

GAME_INDEX=0
for g in "${AVAILABLE_GAMES[@]}"
do
    print_debug $g
    if [ $g == $GAME ]; then 
        break; 
    fi
    GAME_INDEX=`expr $GAME_INDEX + 1`
done

if [ $GAME_INDEX -ge ${#AVAILABLE_GAMES[@]} ]; then
    print_debug "Miss game"
    usage >& 2
    exit 1
fi

if [ -z  ${TARGET_DIR} ]; then
    TARGET_DIR=$HOME/.local/share/playchain_${GAME}
fi

if [[ -n "${IMAGE_PATH}" && ! -f ${IMAGE_PATH} ]]; then
    print_debug "Invalid image path"
    usage >& 2
    exit 1
fi

GAME_TITLE=$(echo $GAME | tr [:lower:] [:upper:])

WELCOME_TEXT=$(cat <<EOF

Welcome!

You are about to install a PlayChain node for game "$GAME_TITLE" based on v$VERSION.

All files will be installed under $TARGET_DIR directory.

Your node will be configured to accept incoming connections from other nodes in
the PlayChain network.

After the installation, it may take some time for your node to download
all history blocks of the PlayChain.

If you wish to uninstall PlayChain node later, you can download this script and
run "sh node-deploy.sh -u".

EOF
)

if [ $UNINSTALL -eq 1 ]; then
    echo
    read -p "WARNING: This will stop PlayChain node for game "$GAME_TITLE" and uninstall it from your system. Uninstall? (y/n) " answer
    if [ "$answer" = "y" ]; then
        uninstall_node
    fi
else
    echo "$WELCOME_TEXT"
    if [ -t 0 ]; then
        # Prompt for confirmation when invoked in tty.
        echo
        read -p "Install? (y/n) " answer
    else
        # Continue installation when invoked via pipe, e.g. curl .. | sh
        answer="y"
        echo
        echo "Starting installation in 10 seconds.."
        sleep 10
    fi
    if [ "$answer" = "y" ]; then
        create_target_dir
        install_build_dependencies

        if [ -f ${IMAGE_PATH} ]; then
            start_node ${IMAGE_PATH}
        else
            download_node $GAME_INDEX
            start_node
        fi
        print_debug "!!! start node result = " $START_NODE_RESULT

        if [[ $START_NODE_RESULT -eq 0 ]]; then
            print_readme > ${TARGET_DIR}/README.md
            cat ${TARGET_DIR}/README.md
            print_success "If you have a big enough pause between starts, PlayChain may take some time to download
            rest history blocks from the PlayChain network."
            print_success "\nInstallation completed!"
        fi
    fi
fi




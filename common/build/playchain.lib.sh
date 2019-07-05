#!/bin/bash

function load_config {
	if [ -z $1 ]; then
		return 0
	fi

	local INPUT_CONFIG_FILE="$1"
	declare -n return_value=$2

	if [[ ! $INPUT_CONFIG_FILE =~ .cfg$ ]]; then
		return_value=${INPUT_CONFIG_FILE}.cfg
	else
		return_value=${INPUT_CONFIG_FILE}
	fi

	if [ ! -f "$return_value" ]; then
		echo "Config file $return_value doesn't exist."
		exit 1
	fi

	source $return_value
}

function clone_repository {

	if [ $# -ne 4 ]
	then
		echo "clone_repository function should take 4 parameters, but passed $#"
		exit
	fi

	local GIT_DIR=_git
	local BUILD_DIR=_build
	local REPOSITORY=$1
	local BRANCH_NAME=$2
	local REPOSITORY_TAG=$3
	declare -n return_value=$4

	echo "Fetch $REPOSITORY from bitbucket... "

	return_value=$GIT_DIR/$REPOSITORY_TAG

	if [ ! -d "$return_value" ]; then
		git clone $REPOSITORY $return_value
	fi
	pushd $return_value
	git fetch origin
	git checkout -f origin/$BRANCH_NAME
	git submodule update --init -f --recursive
	popd
}

function get_temp_dir {

	declare -n return_value=$1

	local DEFAULT_DIR=_tmp

	mkdir -p $DEFAULT_DIR

	return_value=$PWD/$DEFAULT_DIR
}

function get_build_dir {

	declare -n return_value=$1

	local DEFAULT_DIR=_build

	mkdir -p $DEFAULT_DIR

	return_value=$PWD/$DEFAULT_DIR
}

function make_slack_script {

	if [ $# -ne 5 ]
	then
		echo "make_slack_script function should take 4 parameters, but passed $#"
		exit
	fi

	local SLACK_DIR=$1
	local CREATE_DIR=$2
	local SLACK_SCRIPT_NAME=$3
	local SLACK_URI=$4

	declare -n return_value=$5

	local SLACK_SCRIPT_PATH=$CREATE_DIR/$SLACK_SCRIPT_NAME

	if [ -z "$SLACK_DIR" ]; then
		echo "SLACK_DIR must not be null in make_slack_script"
		exit
	fi

	if [ -z "$CREATE_DIR" ]; then
		echo "CREATE_DIR must not be null in make_slack_script"
		exit
	fi

	if [ -z "$SLACK_SCRIPT_NAME" ]; then
		echo "SLACK_SCRIPT_NAME must not be null in make_slack_script"
		exit
	fi

	if [ -z "$SLACK_URI" ]; then
		echo "SLACK_URI must not be null in $CONFIG_FILE file"
		exit
	fi

	if [ ! -d "$CREATE_DIR" ]; then
		mkdir -p $CREATE_DIR
	fi

	cat ${SLACK_DIR}/slack.sh \
		| sed s+'${URL}'+$SLACK_URI+g \
		> $SLACK_SCRIPT_PATH

	chmod a+x $SLACK_SCRIPT_PATH

	echo ">> SLACK_SCRIPT_PATH is $SLACK_SCRIPT_PATH" 
	return_value=$PWD/$SLACK_SCRIPT_PATH
}

function get_scripts_install_dir {

	declare -n return_value=$1

	local DEFAULT_DIR=/etc/monit/bin

	if [ ! -d "$DEFAULT_DIR" ]; then
		mkdir -p $DEFAULT_DIR
	fi

	return_value=$DEFAULT_DIR
}

function get_scripts_dir {

	declare -n return_value=$1

	local DEFAULT_DIR=_monit

	create_dir $DEFAULT_DIR

	return_value=$DEFAULT_DIR
}

function get_config_dir {

	declare -n return_value=$1

	local DEFAULT_DIR=_config

	create_dir $DEFAULT_DIR

	return_value=$DEFAULT_DIR
}

function get_alarm_cpu_usage_percent {
	local cpu_load
	if [ -n "$REMOTE_SERVER_TO_INSTALL" ] && [ -n "$REMOTE_SERVER_USER" ]; then
		cpu_load=$(expr 90 / $(ssh_exec nproc))
	else
		cpu_load=$(expr 90 / $(nproc))
	fi
	cpu_load=$(($cpu_load>75?$cpu_load:75))
	echo $cpu_load
}

function ssh_exec {
	ssh $REMOTE_SERVER_USER@$REMOTE_SERVER_TO_INSTALL "$@"
}

function create_dir {

	if [ -d "$1" ]; then
		rm -r $1
	fi
	mkdir -p $1;
}

function make_sure_dir_exist {

	if [ ! -d "$1" ]; then
		mkdir -p $1
	fi
}

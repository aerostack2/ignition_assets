#!/usr/bin/env bash

function get_path() {
	target=$1
	path_list=$2

	# Check all paths in path_list for specified model
	IFS_bak=$IFS
	IFS=":"
	for possible_path in ${path_list}; do
		if [ -z $possible_path ]; then
			continue
		fi
		# trim \r from path
		possible_path=$(echo $possible_path | tr -d '\r')
		if test -f "${possible_path}/${target}" ; then
			path=$possible_path
			break
		fi
	done
	IFS=$IFS_bak

	echo $path
}

function spawn_model() {
    N=${1:=0}
    model=$2
    x=$3
    y=$4
    z=$5
    Y=$6

	target="${model}/${model}.sdf"
	modelpath="$(get_path ${target} ${IGN_GAZEBO_RESOURCE_PATH})"
    DIR_SCRIPT="${0%/*}"
    python3 ${DIR_SCRIPT}/jinja_gen.py ${modelpath}/${target}.jinja ${modelpath}.. --namespace namespace_${N} --output-file /tmp/${model}_${N}.sdf

    ros2 run ros_ign_gazebo create -file /tmp/${model}_${N}.sdf -x $x -y $y -z $z -Y $Y
}

function start_ign() {
    world=$1

    ign gazebo $world
}

start_ign empty.sdf &
sleep 1
spawn_model 0 quadrotor_base 0 0 0.1 0
spawn_model 1 quadrotor_base 3 0 0.1 0

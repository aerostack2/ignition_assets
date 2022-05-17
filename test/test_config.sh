#!/bin/bash

export RUN_ON_START=1

config=${AEROSTACK2_STACK}/simulation/ignition_assets/test/config.json

${AEROSTACK2_STACK}/simulation/ignition_assets/scripts/run_ign.sh ${config}
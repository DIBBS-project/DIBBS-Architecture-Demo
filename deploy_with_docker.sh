#!/bin/bash
set -x

sudo ./set_up_docker.sh

repos/clone_all.sh
repos/reset_stable.sh

sudo ./run_with_docker.sh

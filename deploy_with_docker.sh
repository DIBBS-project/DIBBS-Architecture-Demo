#!/bin/bash
set -x

./set_up_docker.sh

repos/clone_all.sh

./run_with_docker.sh

#!/bin/bash
set -x

# sudo ./set_up_docker.sh # this is super-sensitive to OS versions nowadays :\

repos/clone_all.sh
yes | repos/reset_stable.sh

sudo ./run_with_docker.sh

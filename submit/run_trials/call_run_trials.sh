#!/bin/bash

SIGFILE1=$1
SIGFILE2=$2
BGFILE1=$3
BGFILE2=$4
SOLARBGFILE1=$5
SOLARBGFILE2=$6
DELTAFILE=$7
SEED=$8
NORM=$9
N=${10}
KEY=${11}

echo $N
echo $KEY

source /data/ana/BSM/IC86_all_energy_solar_WIMP/solar_WIMP_v2//env_nocombo.sh

CMD="/data/user/jlazar/combo37/build/env-shell.sh python /data/ana/BSM/IC86_all_energy_solar_WIMP/solar_WIMP_v2/scripts/4_run_trials.py --sigfile $SIGFILE1 $SIGFILE2 --bgfile $BGFILE1 $BGFILE2 --solar_bgfile $SOLARBGFILE1 $SOLARBGFILE2 --outfile $DELTAFILE -s $SEED --norm $NORM -n $N --key $KEY"
#CMD="/data/user/jlazar/combo37/build/env-shell.sh python /data/ana/BSM/IC86_all_energy_solar_WIMP/solar_WIMP_v2/scripts/3_run_trials.py --sigfile $SIGFILE1 $SIGFILE2 --bgfile $BGFILE1 $BGFILE2 --deltafile $DELTAFILE --seed $SEED --norm ${NORM} -n $N"
echo $CMD
$CMD

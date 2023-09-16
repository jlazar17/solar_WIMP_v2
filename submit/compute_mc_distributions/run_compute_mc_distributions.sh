#! /bin/bash

FLUXFILE=$1
OUTFILE=$2
N=$3
SEED=$4
KEYS=${@:5}

source /data/ana/BSM/IC86_all_energy_solar_WIMP/solar_WIMP_v2//env_nocombo.sh

CMD="/data/user/jlazar/combo37/build/env-shell.sh python /data/ana/BSM/IC86_all_energy_solar_WIMP/solar_WIMP_v2/scripts/2_compute_mc_distributions.py --fluxfile $FLUXFILE --outfile ${OUTFILE} --seed ${SEED} -n ${N} --keys ${KEYS}"
echo $CMD
$CMD

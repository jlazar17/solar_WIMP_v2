# Compute tabulated fluxes

This should take about 5 minutes

```bash
CHANNEL=5
MASS=500
python $SCRIPTSDIR/0_run_charon.py --channel $CHANNEL --mass $MASS --outfile "$DATADIR/$CHANNEL-${MASS}_flux.txt"
```

# Compute the flux for each MC event

These should each take about one minutes

```bash
python $SCRIPTSDIR/1_compute_mc_fluxes.py --mcfile /data/ana/BSM/IC86_all_energy_solar_WIMP/data/point_source_data/IC86_pass2_MC.npy --fluxfile ${DATADIR}/${CHANNEL}-${MASS}_flux.txt --outfile ${DATADIR}/IC86_pass2_MC_fluxes.h5
python $SCRIPTSDIR/1_compute_mc_fluxes.py --mcfile /data/ana/BSM/IC86_all_energy_solar_WIMP/data/oscNext_data/oscNext_simulation_no_muon.h5 --fluxfile ${DATADIR}/${CHANNEL}-${MASS}_flux.txt --outfile ${DATADIR}/oscNext_simulation_no_muon_fluxes.h5
```

# Repeat the last step for the solar atmospheric flux

Once again, this should take about a minute

```bash
python $SCRIPTSDIR/1_compute_mc_fluxes.py --mcfile /data/ana/BSM/IC86_all_energy_solar_WIMP/data/point_source_data/IC86_pass2_MC.npy --fluxfile /data/ana/BSM/IC86_all_energy_solar_WIMP/data/tabulated_flux/SIBYLL2.3_ppMRS_CombinedGHAndHG_H4a.txt --outfile ${DATADIR}/IC86_pass2_MC_fluxes.h5
python $SCRIPTSDIR/1_compute_mc_fluxes.py --mcfile /data/ana/BSM/IC86_all_energy_solar_WIMP/data/oscNext_data/oscNext_simulation_no_muon.h5 --fluxfile /data/ana/BSM/IC86_all_energy_solar_WIMP/data/tabulated_flux/SIBYLL2.3_ppMRS_CombinedGHAndHG_H4a.txt --outfile ${DATADIR}/oscNext_simulation_no_muon_fluxes.h5
```

# Compute the analysis distributions for MC

For best results, this should be run for `-n 50_000` but `-n 5_000` is usually sufficient for checking reproducibility.
If you go the route of `5_000` these should take about 10 minutes and 5 minutes.
Multiply by ten if going the `50_000` route.
In the latter case, it is probably worth submitting these to the cluster.

```bash
python $SCRIPTSDIR/2_compute_mc_distributions.py --fluxfile ${DATADIR}/IC86_pass2_MC_fluxes.h5 --outfile ${DATADIR}/IC86_pass2_MC_simulation_dist.h5 --seed 1996 -n 5_000
python $SCRIPTSDIR/2_compute_mc_distributions.py --fluxfile ${DATADIR}/oscNext_simulation_no_muon_fluxes.h5 --outfile ${DATADIR}/oscNext_simulation_no_muon_simulation_dist.h5 --seed 1112 -n 5_000
```

# Compute the analysis distributions for the scrambled data

These should probably be run around `-n {60-80}` but 20 is sufficient.
As it is, these should each take around 60-90 minutes, sclaing linearly with `n`

```bash
SEED=805; for FILE in `ls /data/ana/BSM/IC86_all_energy_solar_WIMP/data/point_source_data/*exp.npy`; do python $SCRIPTSDIR/3_compute_data_distributions.py --eventsfile $FILE --outfile $DATADIR/pointsource_scrambled_data.h5 -n 20 --seed $SEED; SEED=$(($SEED+1)); done
SEED=8; for FILE in `ls /data/ana/BSM/IC86_all_energy_solar_WIMP/data/oscNext_data/oscNext_data_??_no_muon.h5`; do python $SCRIPTSDIR/3_compute_data_distributions.py --eventsfile $FILE --outfile $DATADIR/oscnext_scrambled_data.h5 -n 20 --seed $SEED; SEED=$(($SEED+1)); done
```

# Run the trials

`10_000` is ideal but once again, `1_000` should be good enough to reproduce the mostly reproduce the sensitivity.
The additional factor of 10 just ensures that we fill out the tail of the distribution and that our TS curves are nice and smooth.
This can be run from the command line, but since you will need to do this for a number of cross sections, I also provide a script for submitting jobs.
This script has cross sections included so you will not need to set them durectly.

```bash
mkdir $LOGSDIR
mkdir $LOGSDIR/error
mkdir $LOGSDIR/output
mkdir $LOGSDIR/submit
mkdir $LOGSDIR/log
python ${SUBMITDIRT}/run_trials/submit_run_trials.py --sigfile ${DATADIR}/IC86_pass2_MC_simulation_dist.h5 ${DATADIR}/oscNext_simulation_no_muon_simulation_dist.h5 --solar_bgfile ${DATADIR}/IC86_pass2_MC_simulation_dist.h5 ${DATADIR}/oscNext_simulation_no_muon_simulation_dist.h5 --bgfile $DATADIR/pointsource_scrambled_data.h5 $DATADIR/oscnext_scrambled_data.h5 -s 925 -n 10_000 --outfile ${DATADIR}/ps_oscnext_trials.h5 --prefix $LOGSDIR
```

# Compute the sensitivity

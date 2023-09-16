import numpy as np
import pycondor

# I found this empirically and it sucks
NORMS_DICT = {
    "5-20": np.logspace(0.6798383138 - 1.0, 0.6798383138 + 1.0, 21),
    "5-50": np.logspace(0.6798383138 - 1.0, 0.6798383138 + 1.0, 21),
    "5-80": np.logspace(0.6798383138 - 1.0, 0.6798383138 + 1.0, 21),
    "5-100": np.logspace(0.8 - 1.0, 0.8 + 1.0, 21),
    "5-200": np.logspace(0.7781512503836436 - 1.0, 0.7781512503836436 + 1.0, 21),
    "5-500": np.logspace(0.47712125471966244 - 1.0, 0.47712125471966244 + 1.0, 21),
    "5-800": np.logspace(0.17609125905568124 - 1.0, 0.17609125905568124 + 1.0, 21),
    "5-1000": np.logspace(0.17609125905568124 - 1.0, 0.17609125905568124 + 1.0, 21),
    "5-2000": np.logspace(0.17609125905568124 - 1.0, 0.17609125905568124 + 1.0, 21),
    "5-5000": np.logspace(0.3979400086720376 - 1.0, 0.3979400086720376 + 1.0, 21),
    "5-10000": np.logspace(1.0 - 1.0, 1.0 + 1.0, 21),
    
    "8-100": np.logspace(-0.3010299956639812 - 1.0, -0.3010299956639812 + 1.0, 21),
    "8-200": np.logspace(-1.0 - 1.0, -1.0 + 1.0, 21),
    "8-500": np.logspace(-1.0 - 1.0, -1.0 + 1.0, 21),
    "8-1000": np.logspace(-0.3979400086720376 - 1.0, -0.3979400086720376 + 1.0, 21),
    "8-2000": np.logspace(-0.22184874961635637 - 1.0, -0.22184874961635637 + 1.0, 21),
    "8-5000": np.logspace(0.8450980400142568 - 1.0, 0.8450980400142568 + 1.0, 21),
    "8-10000": np.logspace(1.4771212547196624 - 1.0, 1.4771212547196624 + 1.0, 21),

    "11-10": np.logspace(-0.09691001301 - 1.0,  -0.09691001301 + 1.0, 21),
    "11-20": np.logspace(-0.3979400086720376 - 1.0,  -0.3979400086720376 + 1.0, 21),
    "11-50": np.logspace(-0.5 - 1.0,  -0.5 + 1.0, 21),
    "11-80": np.logspace(-0.6989700043360187 - 1.0, -0.6989700043360187 + 1.0, 21),
    "11-100": np.logspace(-0.5 - 1.0, -0.5 + 1.0, 21),
    "11-200": np.logspace(-0.5 - 1.0, -0.5 + 1.0, 21),
    "11-500": np.logspace(-1.0 - 1.0, -1.0 + 1.0, 21),
    "11-1000": np.logspace(-0.8 - 1.0, -0.8 + 1.0, 21),
    "11-2000": np.logspace(-0.15 - 1.0, -0.15 + 1.0, 21),
    "11-5000": np.logspace(0.0 - 1.0, 0.0 + 1.0, 21),
    "11-10000": np.logspace(0.5 - 1.0, 0.5 + 1.0, 21),

    "14-20": np.logspace(np.log10(0.05) - 1, np.log10(0.05) + 1, 21),
    "14-50": np.logspace(np.log10(0.02) - 1, np.log10(0.02) + 1, 21),
    "14-100": np.logspace(np.log10(0.02) - 1, np.log10(0.02) + 1, 21),
    "14-200": np.logspace(np.log10(0.02) - 1, np.log10(0.02) + 1, 21),
    "14-500": np.logspace(np.log10(0.005) - 1, np.log10(0.005) + 1, 21),
    "14-1000": np.logspace(np.log10(0.002) - 1, np.log10(0.002) + 1, 21),
    #"14-2000": np.logspace(np.log10(0.005) - 1, np.log10(0.005) + 1, 21),
    "14-5000": np.logspace(-1.0, 1., 21),
    "14-10000": np.logspace(np.log10(5) - 1, np.log10(5) + 1, 21),
}

def initialize_parser():
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument(
        "--sigfile",
        nargs="+",
        required=True
    )
    parser.add_argument(
        "--bgfile",
        nargs="+",
        required=True
    )
    parser.add_argument(
        "--solar_bgfile",
        nargs="+",
        required=True
    )
    parser.add_argument(
        "--outfile",
        type=str,
        required=True
    )
    parser.add_argument(
        "--key",
        type=str,
        required=True
    )
    parser.add_argument(
        "-s",
        "--seed",
        dest="seed",
        type=int,
        required=True,
    )
    parser.add_argument(
        "-n",
        "--n_realizations",
        dest="n",
        default=10000,
        type=int
    )
    parser.add_argument(
        "--norms",
        nargs="+",
    )
    parser.add_argument(
        "--prefix",
        type=str,
        default="/home/jlazar/condor_logs/run_trials/"
    )
    args = parser.parse_args()
    return args

args = initialize_parser()

norms = args.norms
if norms is None:
    norms = np.append(NORMS_DICT[args.key], [0])


output = f"{args.prefix}/output/"
log = f"{args.prefix}/log/"
error = f"{args.prefix}/error/"
submit = f"{args.prefix}/submit/"

xlines = [
    "request_memory = (NumJobStarts is undefined) ? 2 * pow(2, 10) : 1024 * pow(2, NumJobStarts + 1)",
    "periodic_release = (HoldReasonCode =?= 21 && HoldReasonSubCode =?= 1001) || HoldReasonCode =?= 21",
    "periodic_remove = (JobStatus =?= 5 && (HoldReasonCode =!= 34 && HoldReasonCode =!= 21)) || (RequestMemory > 13192)"
]

dagman = pycondor.Dagman("run_trials_dag", submit=submit, verbose=2)
run    = pycondor.Job(
    "run_trials",
    "/data/ana/BSM/IC86_all_energy_solar_WIMP/solar_WIMP_v2/submit/run_trials/call_run_trials.sh", 
    error=error, 
    output=output, 
    log=log, 
    submit=submit, 
    universe="vanilla", 
    notification="never",
    dag=dagman,
    verbose=2,
    extra_lines=xlines
)

for idx, norm in enumerate(norms):
    s = ""
    for f in args.sigfile:
        s += f"{f} "
    for f in args.bgfile:
        s += f"{f} "
    for f in args.solar_bgfile:
        s += f"{f} "
    s += f"{args.outfile} {args.seed} {norm} {args.n} {args.key}"
    run.add_arg(s)
dagman.build()

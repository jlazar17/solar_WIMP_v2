import numpy as np
import pycondor

def initialize_parser():
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument(
        "--fluxfile",
        required=True
    )
    parser.add_argument(
        "--outfile",
        required=True
    )
    parser.add_argument(
        "--seed",
        "-s",
        dest="seed",
        type=int
    )
    parser.add_argument(
        "--keys",
        nargs="+"
    )
    parser.add_argument(
        "-n",
        "--ndays",
        dest="ndays",
        default=10000,
        type=int
    )
    parser.add_argument(
        "--prefix",
        type=str,
        default="/home/jlazar/condor_logs/compute_mc_distributions/"
    )
    args = parser.parse_args()
    return args

if __name__=="__main__":
    args = initialize_parser()
    
    output = f"{args.prefix}/output/"
    log = f"{args.prefix}/log/"
    error = f"{args.prefix}/error/"
    submit = f"{args.prefix}/submit/"
    
    xlines = [
        "request_memory = (NumJobStarts is undefined) ? 10000 : 1024 * pow(2, NumJobStarts + 1)",
        "periodic_release = (HoldReasonCode =?= 21 && HoldReasonSubCode =?= 1001) || HoldReasonCode =?= 21",
        "periodic_remove = (JobStatus =?= 5 && (HoldReasonCode =!= 34 && HoldReasonCode =!= 21)) || (RequestMemory > 13192)"
    ]
    
    dagman = pycondor.Dagman("compute_mc_distributions_dag", submit=submit, verbose=2)
    run = pycondor.Job(
        "compute_mc_distributions",
        "/data/ana/BSM/IC86_all_energy_solar_WIMP/solar_WIMP_v2/submit/compute_mc_distributions/run_compute_mc_distributions.sh",
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
    seed = args.seed
    s = f"{args.fluxfile} {args.outfile} {args.ndays}"
    for key in args.keys:
        run.add_arg(f"{s} {seed} {key}")
        seed += 223
        seed = seed % 2**32
    
    dagman.build()

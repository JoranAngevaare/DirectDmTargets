import DirectDmTargets as dddm
import wimprates as wr
import numpy as np
import argparse
assert wr.__version__ != '0.2.2'
import multiprocessing
import time
import os
import warnings


# # Direct detection of Dark matter using different target materials #
# 
# Author:
# 
# Joran Angevaare <j.angevaare@nikef.nl>
# 
# Date:
# 
# 7 november 2019 
# 
print("run_dddm_multinest.py::\tstart")
parser = argparse.ArgumentParser(description="Running a fit for a certain set of parameters")
parser.add_argument('-sampler', type=str, default='multinest', help="sampler (multinest or nestle)")
parser.add_argument('-mw', type=np.float, default=50., help="wimp mass")
parser.add_argument('-cross_section', type=np.float, default=-45, help="wimp cross-section")
parser.add_argument('-nlive', type=int, default=1024, help="live points used by multinest")
parser.add_argument('-tol', type=float, default=0.1, help="tolerance for opimization (see multinest option dlogz)")
parser.add_argument('-notes', type=str, default="default", help="notes on particular settings")
parser.add_argument('-bins', type=int, default=10, help="the number of energy bins")
parser.add_argument('-nparams', type=int, default=2, help="Number of parameters to fit")
parser.add_argument('-priors_from', type=str, default="Pato_2010", help="Obtain priors from paper <priors_from>")
parser.add_argument('-verbose', type=float, default=0, help="Set to 0 (no print statements), 1 (some print statements) or >1 (a lot of print statements). Set the level of print statements while fitting.")
parser.add_argument('-save_intermediate', type=str, default="no", help="yes / no / default, override internal determination if we need to take into account earth shielding.")
parser.add_argument('-multicore_hash', type=str, default="", help="no / default, override internal determination if we need to take into account earth shielding.")

parser.add_argument('-target', type=str, default='Combined', help="Target material of the detector (Xe/Ge/Ar)")
parser.add_argument('-sub_experiments', nargs='*',
                    help="Extra directories to look for data")
parser.add_argument('--poisson', action='store_true',
                    help="add poisson noise to data")
parser.add_argument('--shielding', action='store_true',
                    help="add shielding to simulation")
parser.add_argument('--save_intermediate', action='store_true',
                    help="add shielding to simulation")
args = parser.parse_args()

if args.sampler == 'multinest':
    # MPI functionality only used for multinest
    try:
        from mpi4py import MPI
        rank = MPI.COMM_WORLD.Get_rank()
    except (ModuleNotFoundError, ImportError) as e:
        warnings.warn('Cannot run in multicore mode as mpi4py is not installed')
        rank = 0
    print(f"info\nn_cores: {multiprocessing.cpu_count()}\npid: {os.getpid()}\nppid: {os.getppid()}\nrank{rank}")
time.sleep(5)

print(f"run_dddm_multinest.py::\tstart for mw = {args.mw}, sigma = "
      f"{args.cross_section}. Fitting {args.nparams} parameters")

dddm.experiment[args.target] = {'type': 'combined'}
stats = dddm.CombinedInference(tuple(args.sub_experiments),
                               args.target,
                               args.verbose,
                               do_init=False)
update_config = {
    'mw': np.log10(args.mw),
    'sigma': args.cross_section,
    'sampler': args.sampler,
    'poisson': args.poisson,
    'notes': args.notes,
    'n_energy_bins': args.bins,
    'save_intermediate': args.save_intermediate,
    'fit_parameters': stats.known_parameters[:args.nparams],
    'nlive': args.nlive,
    'tol': args.tol}

stats.set_prior(args.priors_from)
stats.config['prior']['log_mass'] = {
    'range': [int(np.log10(args.mw)) - 2.5, int(np.log10(args.mw)) + 3.5],
    'prior_type': 'flat'}
stats.config['prior']['log_cross_section'] = {
    'range': [int(args.cross_section) - 7, int(args.cross_section) + 5],
    'prior_type': 'flat'}
stats.config['prior']['log_mass']['param'] = stats.config['prior']['log_mass']['range']
stats.config['prior']['log_cross_section']['param'] = stats.config['prior']['log_cross_section']['range']

stats.config.update(update_config)
update_keys = list(update_config.keys())
update_keys.append('prior')
stats.set_models()
update_keys.append('halo_model')

stats.copy_config(update_keys)
stats.print_before_run()


if args.multicore_hash != "":
    stats.get_save_dir(hash=args.multicore_hash)
    stats.get_tmp_dir(hash=args.multicore_hash)
if stats.config['sampler'] == 'multinest':
    stats.run_multinest()
elif stats.config['sampler'] == 'nestle':
    stats.run_nestle()
if args.multicore_hash == "" or (args.sampler == 'multinest' and rank == 0):
    stats.save_results()
    stats.save_sub_configs()
assert stats.log_dict['did_run']



print(f"run_dddm_multinest.py::\tfinished for mw = {args.mw}, sigma = {args.cross_section}")
print("finished, bye bye")

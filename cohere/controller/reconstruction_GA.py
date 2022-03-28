# #########################################################################
# Copyright (c) , UChicago Argonne, LLC. All rights reserved.             #
#                                                                         #
# See LICENSE file.                                                       #
# #########################################################################


"""
This module controls the genetic algoritm process.
"""

import numpy as np
import os
import cohere.controller.reconstruction_multi as multi
import cohere.utilities.utils as ut
import multiprocessing as mp
from multiprocessing import Process, Queue
import shutil
import importlib
import cohere.controller.phasing as calc


__author__ = "Barbara Frosik"
__copyright__ = "Copyright (c) 2016, UChicago Argonne, LLC."
__docformat__ = 'restructuredtext en'
__all__ = ['Generation.next_gen',
           'Generation.get_data',
           'Generation.get_gmask',
           'Generation.order,'
           'Generation.breed_one',
           'Generation.breed',
           'reconstruction']


def set_lib(pkg, ndim=None):
    global dvclib
    if pkg == 'af':
        if ndim == 1:
            dvclib = importlib.import_module('cohere.lib.aflib').aflib1
        elif ndim == 2:
            dvclib = importlib.import_module('cohere.lib.aflib').aflib2
        elif ndim == 3:
            dvclib = importlib.import_module('cohere.lib.aflib').aflib3
        else:
            raise NotImplementedError
    elif pkg == 'cp':
        dvclib = importlib.import_module('cohere.lib.cplib').cplib
    elif pkg == 'np':
        dvclib = importlib.import_module('cohere.lib.nplib').nplib
    calc.set_lib(dvclib, pkg=='af')


def set_ga_defaults(pars):
    if 'reconstructions' not in pars:
        pars['reconstructions'] = 1

    if 'ga_generations' not in pars:
        pars['ga_generations'] = 1

    # check if pc feature is on
    if 'pc' in pars['algorithm_sequence'] and 'pc_interval' in pars:
        if not 'ga_gen_pc_start' in pars:
            pars['ga_gen_pc_start'] = 0
            pars['ga_gen_pc_start'] = min(pars['ga_gen_pc_start'], pars['ga_generations']-1)

    if 'ga_fast' not in pars:
        pars['ga_fast'] = True

    if 'ga_metrics' not in pars:
        pars['ga_metrics'] = ['chi'] * pars['ga_generations']
    else:
        metrics = pars['ga_metrics']
        if len(metrics) == 1:
            metrics = metrics * pars['ga_generations']
        elif len(metrics) < pars['ga_generations']:
            metrics = metrics + ['chi'] * (pars['ga_generations'] - len(metrics))
    pars['ga_metrics'] = metrics

    ga_reconstructions = []
    if 'ga_cullings' in pars:
        worst_remove_no = pars['ga_cullings']
        if len(worst_remove_no) < pars['ga_generations']:
            worst_remove_no = worst_remove_no + [0] * (pars['ga_generations'] - len(worst_remove_no))
    else:
        worst_remove_no = [0] * pars['ga_generations']
    pars['worst_remove_no'] = worst_remove_no
    # calculate how many reconstructions should continue
    reconstructions = pars['reconstructions']
    for culling in worst_remove_no:
        reconstructions = reconstructions - culling
        if reconstructions <= 0:
            return 'culled down to 0 reconstructions, check configuration'
        ga_reconstructions.append(reconstructions)
    pars['ga_reconstructions'] = ga_reconstructions

    if 'shrink_wrap_threshold' in pars:
        shrink_wrap_threshold = pars['shrink_wrap_threshold']
    else:
        shrink_wrap_threshold = .1
    if 'ga_shrink_wrap_thresholds' in pars:
        ga_shrink_wrap_thresholds = pars['ga_shrink_wrap_thresholds']
        if len(ga_shrink_wrap_thresholds) == 1:
            ga_shrink_wrap_thresholds = ga_shrink_wrap_thresholds * pars['ga_generations']
        elif len(ga_shrink_wrap_thresholds) < pars['ga_generations']:
            ga_shrink_wrap_thresholds = ga_shrink_wrap_thresholds + [shrink_wrap_threshold] * (pars['ga_generations'] - len(ga_shrink_wrap_thresholds))
    else:
        ga_shrink_wrap_thresholds = [shrink_wrap_threshold] * pars['ga_generations']
    pars['ga_shrink_wrap_thresholds'] = ga_shrink_wrap_thresholds

    if 'shrink_wrap_gauss_sigma' in pars:
        shrink_wrap_gauss_sigma = pars['shrink_wrap_gauss_sigma']
    else:
        shrink_wrap_gauss_sigma = .1
    if 'ga_shrink_wrap_gauss_sigmas' in pars:
        ga_shrink_wrap_gauss_sigmas = pars['ga_shrink_wrap_gauss_sigmas']
        if len(ga_shrink_wrap_gauss_sigmas) == 1:
            ga_shrink_wrap_gauss_sigmas = ga_shrink_wrap_gauss_sigmas * pars['ga_generations']
        elif len(pars['ga_shrink_wrap_gauss_sigmas']) < pars['ga_generations']:
            ga_shrink_wrap_gauss_sigmas = ga_shrink_wrap_gauss_sigmas + [shrink_wrap_gauss_sigma] * (pars['ga_generations'] - len(ga_shrink_wrap_gauss_sigmas))
    else:
        ga_shrink_wrap_gauss_sigmas = [shrink_wrap_gauss_sigma] * pars['ga_generations']
    pars['ga_shrink_wrap_gauss_sigmas'] = ga_shrink_wrap_gauss_sigmas

    if 'ga_breed_modes' not in pars:
        pars['ga_breed_modes'] = ['sqrt_ab'] * pars['ga_generations']
    else:
        ga_breed_modes = pars['ga_breed_modes']
        if len(ga_breed_modes) == 1:
            ga_breed_modes = ga_breed_modes * pars['ga_generations']
        elif len(ga_breed_modes) < pars['ga_generations']:
            ga_breed_modes = ga_breed_modes + ['sqrt_ab'] * (pars['ga_generations'] - len(ga_breed_modes))
    pars['ga_breed_modes'] = ga_breed_modes

    if 'ga_lowpass_filter_sigmas' in pars:
        pars['low_resolution_generations'] = len(pars['ga_lowpass_filter_sigmas'])
    else:
        pars['low_resolution_generations'] = 0

    if pars['low_resolution_generations'] > 0:
        if 'low_resolution_alg' not in pars:
            pars['low_resolution_alg'] = 'GAUSS'

    return pars



def order_dirs(dirs, evals, metric):
    """
    Orders results in generation directory in subdirectories numbered from 0 and up, the best result stored in the '0' subdirectory. The ranking is done by numbers in evals list, which are the results of the generation's metric to the image array.

    Parameters
    ----------
    dirs : list
        list of directories where the reconstruction results files are saved
    evals : list
        list of evaluation of the results in the directories from the dirs list. The evaluation is a number calculated for metric configured for this generation

    Returns
    -------
    nothing
    """
    # ranks keeps indexes of reconstructions from best to worst
    # for most of the metric types the minimum of the metric is best, but for
    # 'summed_phase' and 'area' it is oposite, so reversing the order
    ranks = np.argsort(evals).tolist()
    if metric == 'summed_phase' or metric == 'area':
        ranks.reverse()

    # all the generation directories are in the same parent directory
    parent_dir = os.path.abspath(os.path.join(dirs[0], os.pardir))
    rank_dirs = []
    # append "_<rank>" to each result directory name
    for i in range(len(ranks)):
        dest = os.path.join(parent_dir, str(i) + '_' + str(ranks[i]))
        shutil.move(dirs[i], dest)
        rank_dirs.append(dest)

    # remove the number preceding rank from each directory name, so the directories are numbered
    # according to rank
    for dir in rank_dirs:
        last_sub = os.path.basename(dir)
        dest = os.path.join(parent_dir, last_sub.split('_')[-1])
        shutil.move(dir, dest)


def order_processes(proc_metrics, metric_type):
    """
    Orders results in generation directory in subdirectories numbered from 0 and up, the best result stored in the '0' subdirectory. The ranking is done by numbers in evals list, which are the results of the generation's metric to the image array.

    Parameters
    ----------
    dirs : list
        list of directories where the reconstruction results files are saved
    evals : list
        list of evaluation of the results in the directories from the dirs list. The evaluation is a number calculated for metric configured for this generation

    Returns
    -------
    nothing
    """
    ranked_proc = sorted(proc_metrics.items(), key=lambda x: x[1], reverse=False)

    # ranks keeps indexes of reconstructions from best to worst
    # for most of the metric types the minimum of the metric is best, but for
    # 'summed_phase' and 'area' it is oposite, so reversing the order
    if metric_type == 'summed_phase' or metric_type == 'area':
        ranked_proc.reverse()
    return ranked_proc


def cull(lst, no_left):
    if len(lst) <= no_left:
        return lst
    else:
        return lst[0:no_left]


def reconstruction(lib, conf_file, datafile, dir, devices):
    """
    This function controls reconstruction utilizing genetic algorithm.

    Parameters
    ----------
    proc : str
        processor to run on (cpu, opencl, or cuda)

    conf_file : str
        configuration file with reconstruction parameters

    datafile : str
        name of the file with initial data

    dir : str
        a parent directory that holds the generations. It can be experiment directory or scan directory.

    devices : list
        list of GPUs available for this reconstructions

    Returns
    -------
    nothing
    """
    pars = ut.read_config(conf_file)
    pars = set_ga_defaults(pars)

    if 'save_dir' in pars:
        save_dir = pars['save_dir']
    else:
        filename = conf_file.split('/')[-1]
        save_dir = os.path.join(dir, filename.replace('config_rec', 'results_phasing'))

    generations = pars['ga_generations']
    reconstructions = pars['reconstructions']

    if reconstructions < 2:
        print ("GA not implemented for a single reconstruction")

    # the cupy does not run correctly with multiprocessing, but limiting number of runs to available devices will work as temporary fix
    if pars['ga_fast']:  # the number of processes is the same as available GPUs (can be same GPU if can fit more recs)
        if lib == 'af' or lib == 'cpu' or lib == 'opencl' or lib == 'cuda':
            if datafile.endswith('tif') or datafile.endswith('tiff'):
                try:
                    data = ut.read_tif(datafile)
                except:
                    print('could not load data file', datafile)
                    return
            elif datafile.endswith('npy'):
                try:
                    data = np.load(datafile)
                except:
                    print('could not load data file', datafile)
                    return
            else:
                print('no data file found')
                return
            set_lib('af', len(data.shape))
            if lib != 'af':
                dvclib.set_backend(lib)
        else:
            set_lib(lib)

        reconstructions = min(reconstructions, len(devices))
        workers = [calc.Rec(pars, datafile) for _ in range(reconstructions)]
        processes = {}

        for worker in workers:
            worker_qin = Queue()
            worker_qout = Queue()
            process = Process(target=worker.fast_ga, args=(worker_qin, worker_qout))
            process.start()
            processes[process.pid] = [worker_qin, worker_qout]

        prev_dirs = None
        for g in range(generations):
            print ('starting generation',g)
            if g == 0:
                for pid in processes:
                    worker_qin = processes[pid][0]
                    worker_qin.put(('init_dev', devices.pop()))
                bad_processes = []
                for pid in processes:
                    worker_qout = processes[pid][1]
                    ret = worker_qout.get()
                    if ret < 0:
                        worker_qin = processes[pid][0]
                        worker_qin.put('done')
                        bad_processes.append(pid)
                # remove bad processes from dict (in the future we may reuse them)
                for pid in bad_processes:
                    processes.pop(pid)
            for pid in processes:
                worker_qin = processes[pid][0]
                if prev_dirs is None:
                    prev_dir = None
                else:
                    prev_dir = prev_dirs[pid]
                worker_qin.put(('init', prev_dir, g))
            for pid in processes:
                worker_qout = processes[pid][1]
                ret = worker_qout.get()
            if g > 0:
                for pid in processes:
                    worker_qin = processes[pid][0]
                    worker_qin.put('breed')
                for pid in processes:
                    worker_qout = processes[pid][1]
                    ret = worker_qout.get()
            for pid in processes:
                worker_qin = processes[pid][0]
                worker_qin.put('iterate')
            bad_processes = []
            for pid in processes:
                worker_qout = processes[pid][1]
                ret = worker_qout.get()
                if ret < 0:
                    worker_qin = processes[pid][0]
                    worker_qin.put('done')
                    bad_processes.append(pid)
            # remove bad processes from dict (in the future we may reuse them)
            for pid in bad_processes:
                processes.pop(pid)
            # get metric, i.e the goodness of reconstruction from each run
            proc_metrics = {}
            metric_type = pars['ga_metrics'][g]
            for pid in processes:
                worker_qin = processes[pid][0]
                worker_qin.put(('get_metric', metric_type))
            for pid in processes:
                worker_qout = processes[pid][1]
                metric = worker_qout.get()
                proc_metrics[pid] = metric
            # order processes by metric
            proc_ranks = order_processes(proc_metrics, metric_type)
            # cull
            culled_proc_ranks = cull(proc_ranks, pars['ga_reconstructions'][g])
            # remove culled processes from list (in the future we may reuse them)
            for i in range(len(culled_proc_ranks), len(proc_ranks)):
                pid = proc_ranks[i][0]
                worker_qin = processes[pid][0]
                worker_qin.put('done')
                processes.pop(pid)
            # save results, we may modify it later to save only some
            gen_save_dir = os.path.join(save_dir, 'g_' + str(g))
            prev_dirs = {}
            for i in range(len(culled_proc_ranks)):
                pid = culled_proc_ranks[i][0]
                worker_qin = processes[pid][0]
                worker_qin.put(('save_res', os.path.join(gen_save_dir, str(i))))
                prev_dirs[pid] = os.path.join(gen_save_dir, str(i))
            for pid in processes:
                worker_qout = processes[pid][1]
                ret = worker_qout.get()
            if len(processes) == 0:
                break
        for pid in processes:
            worker_qin = processes[pid][0]
            worker_qin.put('done')
    else:   # not fast GA
        rec = multi
        prev_dirs = []
        q = Queue()
        for _ in range(reconstructions):
            prev_dirs.append(None)
        for g in range(generations):
            print ('starting generation',g)
            gen_save_dir = os.path.join(save_dir, 'g_' + str(g))
            metric_type = pars['ga_metrics'][g]
            p = Process(target=rec.multi_rec, args=(lib, gen_save_dir, devices, reconstructions, pars, datafile, prev_dirs, metric_type, g, q))
            p.start()
            p.join()

            prev_dirs, evals = q.get()
            # results are saved in a list of directories - save_dir
            # it will be ranked, and moved to temporary ranked directories
            order_dirs(prev_dirs, evals, metric_type)
            reconstructions = pars['ga_reconstructions'][g]
            prev_dirs = cull(prev_dirs, reconstructions)

    print('done gen')

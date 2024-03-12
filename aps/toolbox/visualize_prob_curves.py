import sys
import numpy as np
import matplotlib.pyplot as plt
import xtgeo

from pandas import DataFrame
from pathlib import Path
from aps.utils.ymlUtils import get_text_value, get_int_value, get_list, readYml, get_bool_value
from aps.utils.constants.simple import Debug


def run(params):
    if not sys.warnoptions:
        # NOTE: This will remove python warnings
        import warnings
        warnings.simplefilter("ignore")

    project = params['project']
    model_file_name = params['model_file_name']
    params = read_model_file(model_file_name)
    if params['plot_vpc']:
        vpc, maxnvalues, zone_name = read_vpc(params)
        plot_vpc(vpc, maxnvalues, zone_name)

    else:
        grid_model_name = params['grid_model_name']
        blocked_well_set_name = params['bw_set_name']
        well_names = params['well_list']
        prob_log_names = params['prob_log_names']
        max_zone_number = params['max_zone_number']
        zone_log_name = params['zone_log_name']


        plot_probability_logs(
            project,
                grid_model_name,
                blocked_well_set_name,
                well_names,
                prob_log_names,
                zone_log_name,
                max_zone_number)


def plot_probability_logs(
        project,
        grid_model_name: str,
        blocked_well_set_name: str,
        well_list: list,
        prob_log_names: list,
        zone_log_name: str,
        max_zone_number: int,
    ):
    nwells = len(well_list)
    nlogs = len(prob_log_names)
    lognames = prob_log_names.copy()
    lognames.append(zone_log_name)
    rel_width = np.zeros(2*nwells, dtype= np.float32)
    for i in range(2*nwells):
        n = i + 1
        if (n//2)*2 == n:
            rel_width[i] = 1
        else:
            rel_width[i] = 0.4

    fig, axs = plt.subplots(nrows=1,
                            ncols=2*nwells,
                            sharey='row',
                            gridspec_kw= dict(width_ratios = rel_width),
                            constrained_layout=True)
    axs[0].invert_yaxis()
    axs[0].margins(y=0)

    axs[0].set_axisbelow(False)
    xticks_zone = np.arange(0, max_zone_number+1, 1)
    xticks_prob = np.arange(0, 1.001, 0.5)
    print("Read blocked well data for probability logs:")
    for m, well_name in enumerate(well_list):
        print(f" -Well: {well_name}  ")
        try:
            bw_well = xtgeo.blockedwell_from_roxar(project,
                grid_model_name,
                blocked_well_set_name,
                well_name,
                lognames=lognames)
        except:
            raise IOError(f"Well:{well_name} may not be blocked before running this script?")

        cumulative_prob_refined, z_indices, z_values, zone_log_values_refined = \
            cumulative_prob_logs(bw_well.dataframe, prob_log_names, zone_log_name)
        plot_number_zone_log = 2*m
        plot_number_prob_logs = 2*m + 1

        # Plot prob logs
        for n in range(nlogs):
            logname = prob_log_names[n]
            axs[plot_number_prob_logs].fill_betweenx(z_values, cumulative_prob_refined[n,:], label=logname , zorder=-n)
            axs[plot_number_prob_logs].set_title(well_name)
            axs[plot_number_prob_logs].set_xlim(-0.01, 1.01)
            axs[plot_number_prob_logs].set_xticks(xticks_prob)
            axs[plot_number_prob_logs].grid(True)

        # Plot zone log
        axs[plot_number_zone_log].plot(zone_log_values_refined, z_values)
        axs[plot_number_zone_log].set_title("Zone")
        axs[plot_number_zone_log].set_xlim(0, max_zone_number+0.1)
        axs[plot_number_zone_log].set_xticks(xticks_zone)
        axs[plot_number_zone_log].grid(True)
    plt.legend(loc="upper left", bbox_to_anchor=(1.1, 1.0))
    plt.show()

def plot_vpc(vpc, nz, zone_name):
    nfacies = len(vpc.keys())
    # Calculate cumulative prob
    cumprob = np.zeros((nfacies,nz), dtype=np.float32)
    facies_list = list(vpc.keys())
    fname = facies_list[0] 
    z_values = vpc[fname][:,0]  
    cumprob[0,:] = vpc[fname][:,1]  
    for n in range(1,nfacies):
        fname = facies_list[n] 
        cumprob[n,:] = cumprob[n-1,:] + vpc[fname][:,1]

    # Refinement
    refinementfactor = 10
    nval_refined = nz * refinementfactor
    dz = 1.0/refinementfactor
    z_refined = np.arange(0, nz, dz)
    cumprob_refined = np.zeros((nfacies, nval_refined), dtype=np.float32)

    indx = 0
    for n in range(nfacies):
        indx = 0
        for k in range(nz):
            p = cumprob[n,k]
            for j in range(refinementfactor):
                cumprob_refined[n,indx] = p
                indx += 1

    fig, axs = plt.subplots()
    axs.invert_yaxis()
    axs.margins(y=0)

    axs.set_axisbelow(False)
    xticks_prob = np.arange(0, 1.001, 0.1)
    # Plot prob logs
    for n in range(nfacies):
        fname = facies_list[n]
        cum_prob_values = cumprob_refined[n,:]
        axs.fill_betweenx(z_refined, cum_prob_values, label=fname , zorder=-n)
        axs.set_title(f"VPC {zone_name}")
        axs.set_xlim(-0.01, 1.01)
        axs.set_xticks(xticks_prob)
        axs.grid(True)

    plt.legend(loc="upper left", bbox_to_anchor=(1.1, 1.0))
    plt.show()


def cumulative_prob_logs(dataframe: DataFrame, prob_log_names: list, zone_log_name: str, refinement_factor: int = 10):
    bw_df = dataframe
    if prob_log_names is None or len(prob_log_names) == 0:
        return None, None, None

    prob_log = bw_df.loc[:, prob_log_names[0]]
    zone_log_val = bw_df.loc[:, zone_log_name]
    num_val = len(prob_log)
    num_logs = len(prob_log_names)
    sumprob = np.zeros(num_val, dtype=np.float32)
    cum_prob = np.zeros((num_logs, num_val), dtype=np.float32)
    for n, logname in enumerate(prob_log_names):
        prob_log = bw_df.loc[:, logname]
        sumprob = sumprob + prob_log
        cum_prob[n,:] = sumprob[:]

    num_val_refined = num_val * refinement_factor
    refined_cum_prob = np.zeros((num_logs, num_val_refined), dtype=np.float32)
    z_indices = np.zeros(num_val_refined, dtype=np.int32)
    zone_log_val_refined = np.zeros(num_val_refined, dtype=np.int32)
    indx = 0
    for j in range(num_val):
        for i in range(refinement_factor):
            refined_cum_prob[:,indx] = cum_prob[:,j]
            zone_log_val_refined[indx] = zone_log_val[j]
            indx += 1
    z_indices = np.arange(0, num_val_refined)
    z_values = np.arange(0, num_val, 1.0/refinement_factor)

    return refined_cum_prob, z_indices, z_values, zone_log_val_refined



def read_model_file(model_file_name):
    suffix = Path(model_file_name).suffix.lower().strip('.')
    if suffix in ['yaml', 'yml']:
        param_dict = _read_model_file_yml(model_file_name)
    elif suffix == 'xml':
            raise ValueError(f"No xml file format implemented for {__name__}   ")
    else:
        raise ValueError(f"Model file name: {model_file_name}  must be 'yml' format")
    return param_dict

def _read_model_file_yml(model_file_name):
    print(f'Read model file: {model_file_name}')
    spec_all = readYml(model_file_name)

    kw_parent = 'PlotProbLogs'
    spec = spec_all[kw_parent] if kw_parent in spec_all else None
    if spec is None:
        raise ValueError(f"Missing keyword: {kw_parent} ")

    params = {}
    plot_vpc = get_bool_value(spec, 'PlotEstimatedVPC', False)
    params['plot_vpc'] = plot_vpc 
    if not plot_vpc:
        params['debug_level'] = get_int_value(spec, kw_parent, 'DebugLevel', has_default=True, default_value=Debug.OFF)
        params['grid_model_name'] = get_text_value(spec, kw_parent, 'GridModelName')
        params['bw_set_name']  = get_text_value(spec, kw_parent, 'BlockedWellSetName')
        params['zone_log_name'] = get_text_value(spec, kw_parent, 'ZoneLogName')
        params['max_zone_number'] = get_int_value(spec, kw_parent, 'MaxZoneNumber')
        params['well_list'] = get_list(spec, kw_parent, 'WellList')
        params['prob_log_names']  = get_list(spec, kw_parent, 'ProbLogNames')
    else:
        params['average_prob_log_prefix'] = get_text_value(spec, kw_parent, 'AverageProbLogPrefix')
        params['average_prob_log_file_path'] = get_text_value(spec, kw_parent, 'AverageProbLogFilePath')
        params['facies_names'] = get_list(spec, kw_parent, 'Facies')
        params['zone_name'] = get_text_value(spec, kw_parent, 'ZoneName')
    return params

def read_vpc(params: dict):
    facies_list = params['facies_names']
    zone_name = params['zone_name'] 
    prefix = params['average_prob_log_prefix']
    path = params['average_prob_log_file_path']
    
    maxnvalues = 0
    vpc_dict ={}
    for fname in facies_list:
        filename = path + "/" + prefix + "_" + fname
        with open(filename, "r") as file:
            lines = file.readlines()
        nvalues = len(lines)
        if maxnvalues < nvalues:
            maxnvalues = nvalues
        vpc_dict[fname] = None

    for fname in facies_list:
        vpc_dict[fname] = np.zeros((maxnvalues, 2), dtype=np.float32)

    for fname in facies_list:
        filename = path + "/" + prefix + "_" + fname
        print(f"Read file: {filename}")
        with open(filename, "r") as file:
            lines = file.readlines()
        x = [] 
        y = [] 
        for line in lines:
            words = line.split(" ")
            x.append(float(words[0]))
            y.append(float(words[1]))
        vpc_dict[fname][:,0]   = np.array(x)
        vpc_dict[fname][:,1]   = np.array(y)
    return vpc_dict, maxnvalues, zone_name

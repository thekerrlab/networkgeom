from netpyne import specs, sim
try:
	from __main__ import *  # import SimConfig object with params from parent module
except:
	from config import *  # if no simConfig in parent module, import directly from tut8_cfg module
import math

# Network parameters - object of class NetParams to store the network parameters
netParams = specs.NetParams()

## Constants/Variables
# Generate ranges from geometry
input_x_range = [0,cfg.input_horiz_len]
input_y_range = [cfg.input_vert_loc,cfg.input_vert_loc]
input_z_range = [0,cfg.input_horiz_len]
middle_x_range = [0,cfg.middle_horiz_len]
middle_y_range = [cfg.middle_vert_loc,cfg.middle_vert_loc]
middle_z_range = [0,cfg.middle_horiz_len]
output_x_range = [0,cfg.output_horiz_len]
output_y_range = [cfg.output_vert_loc,cfg.output_vert_loc]
output_z_range = [0,cfg.output_horiz_len]

# Set some netParam variables
netParams.propVelocity = cfg.propagation_velocity	# propagation velocity (um/ms)
netParams.probLengthConst = cfg.prob_length_const 	# length constant for conn probability (um)
# Constants for Weight and probability
netParams.max_prob_const = cfg.max_conn_probability
netParams.prob_dist_factor = cfg.exp_dist_factor_prob

## Population parameters
netParams.popParams['Input'] = {'cellModel': 'Izhi', 'cellType': 'In', 'xRange': input_x_range,\
 	'yRange': input_y_range, 'zRange': input_z_range, 'numCells': cfg.input_pop_size}
netParams.popParams['Izhi_excit'] = {'cellModel': 'Izhi', 'cellType': 'E', 'xRange': middle_x_range,\
 	'yRange': middle_y_range, 'zRange': middle_z_range, 'numCells': cfg.middle_exc_pop_size}
netParams.popParams['Izhi_inhib'] = {'cellModel': 'Izhi', 'cellType': 'I', 'xRange': middle_x_range,\
 	'yRange': middle_y_range, 'zRange': middle_z_range, 'numCells': cfg.middle_inhib_pop_size}
netParams.popParams['Output'] = {'cellModel': 'Izhi', 'cellType': 'Out', 'xRange': output_x_range,\
 	'yRange': output_y_range, 'zRange': output_z_range, 'numCells': cfg.output_pop_size}

# Izhi cell parameters used in cell properties
izhiParams = {} # initialise dictionary
izhiParams['RS'] = {'mod':'Izhi2007b', 'C':1, 'k':0.7, 'vr':-60, 'vt':-40, 'vpeak':35, 'a':0.03, 'b':-2, 'c':-50, 'd':100, 'celltype':1}
izhiParams['LTS'] = {'mod':'Izhi2007b', 'C':1, 'k':1.0, 'vr':-56, 'vt':-42, 'vpeak':40, 'a':0.03, 'b':8, 'c':-53, 'd':20, 'celltype':4}
izhiParams['FS'] = {'mod':'Izhi2007b', 'C':0.2, 'k':1.0, 'vr':-55, 'vt':-40, 'vpeak':25, 'a':0.2, 'b':-2, 'c':-45, 'd':-55, 'celltype':5}

# STDP parameters
STDPparams = {'hebbwt': 0.00001, 'antiwt':-0.00001, 'wmax': 50, 'RLon': 1 , 'RLhebbwt': 0.001, 'RLantiwt': -0.000, \
    'tauhebb': 10, 'RLwindhebb': 50, 'useRLexp': 0, 'softthresh': 0, 'verbose':0}

## Cell property rules
# Input cells (Izhi)
cellRule = {'conds': {'cellType': 'In', 'cellModel': 'Izhi'}, 'secs': {}}
cellRule['secs']['soma'] = {'geom': {}, 'pointps': {}}    # soma properties
cellRule['secs']['soma']['geom'] = {'diam': 10, 'L': 10, 'cm': 31.831} # soma geometry
cellRule['secs']['soma']['pointps']['Izhi'] = izhiParams['RS']
netParams.cellParams['Input'] = cellRule

# Middle layer Excitory cells (Izhi)
cellRule = {'conds': {'cellType': 'E', 'cellModel': 'Izhi'}, 'secs': {}}
cellRule['secs']['soma'] = {'geom': {}, 'pointps': {}}    # soma properties
cellRule['secs']['soma']['geom'] = {'diam': 10, 'L': 10, 'cm': 31.831} # soma geometry
cellRule['secs']['soma']['pointps']['Izhi'] = izhiParams['RS'] # make E = RS
netParams.cellParams['Izhi_excit'] = cellRule

# Middle layer Inhibitory cells (Izhi)
cellRule = {'conds': {'cellType': 'I', 'cellModel': 'Izhi'}, 'secs': {}}
cellRule['secs']['soma'] = {'geom': {}, 'pointps': {}}    # soma properties
cellRule['secs']['soma']['geom'] = {'diam': 10, 'L': 10, 'cm': 31.831} # soma geometry
cellRule['secs']['soma']['pointps']['Izhi'] = izhiParams['FS'] # make I = RS
netParams.cellParams['Izhi_inhib'] = cellRule

# Output cells (Izhi)
cellRule = {'conds': {'cellType': 'Out', 'cellModel': 'Izhi'}, 'secs': {}}
cellRule['secs']['soma'] = {'geom': {}, 'pointps': {}}    # soma properties
cellRule['secs']['soma']['geom'] = {'diam': 10, 'L': 10, 'cm': 31.831} # soma geometry
cellRule['secs']['soma']['pointps']['Izhi'] = izhiParams['RS']
netParams.cellParams['Output'] = cellRule

## Synaptic mechanism parameters
#netParams.synMechParams['bkg'] = {'mod': 'Exp2Syn', 'tau1': 0.8, 'tau2': 5.3, 'e': 0}  # NMDA/AMPA synaptic mechanism
netParams.synMechParams['exc'] = {'mod': 'Exp2Syn', 'tau1': 0.8, 'tau2': 5.3, 'e': 0}  # NMDA/AMPA synaptic mechanism
netParams.synMechParams['inh'] = {'mod': 'Exp2Syn', 'tau1': 0.6, 'tau2': 8.5, 'e': -75}  # GABA synaptic mechanism
# netParams.synMechParams['AMPA'] = {'mod': 'ExpSyn', 'tau': 0.1, 'e': 0}
# mechanism parameters taken from netpyne's arm example:
#netParams.synMechParams['AMPA'] = {'mod': 'Exp2Syn', 'tau1': 0.05, 'tau2': 5.3, 'e': 0} # AMPA
#netParams.synMechParams['NMDA'] = {'mod': 'Exp2Syn', 'tau1': 0.15, 'tau2': 1.50, 'e': 0} # NMDA
#netParams.synMechParams['GABA'] = {'mod': 'Exp2Syn', 'tau1': 0.07, 'tau2': 9.1, 'e': -80} # GABAA


# Stimulation parameters
netParams.stimSourceParams['Input'] = {'type': 'NetStim', 'interval': cfg.backgroundStimDelayPeriod, 'number': cfg.backgroundStimNumber, 'start': 0, 'noise': 0}
#netParams.stimSourceParams['Input'] = {'type': 'IClamp', 'del': 0, 'dur': 5, 'amp': 1}
netParams.stimTargetParams['Input->input'] = {'source': 'Input', 'sec':'soma', 'loc': 0.5, 'conds': {'cellType': ['In'], 'cellList': sim.forageCellList}, 'synMech': 'exc'}
#netParams.stimTargetParams['bkg->input'] = {'source': 'bkg', 'conds': {'cellType': ['In'], 'cellList': forageCellList}, 'weight': cfg.backgroundStimWeight, 'delay': 0, 'synMech': 'exc'}
#netParams.stimTargetParams['bkg->input'] = {'source': 'bkg', 'conds': {'cellType': ['In'], 'cellList': forageCellList}, 'weight': cfg.backgroundStimWeight, 'delay': 0, 'synMech': 'exc'}

## Cell connectivity rules
# Input to middle
netParams.connParams['In->EI'] = {
    'preConds': {'cellType': 'In'},
    'postConds': {'cellType': ['E', 'I']},
	'weight': cfg.input_weight,
    'probability': 'max_prob_const*exp(-prob_dist_factor*dist_3D/probLengthConst)', # probability of connection
    'delay': 'dist_3D/propVelocity',                                        # delay min=0.2, mean=13.0, var = 1.4
    'threshold': 10,                                                        # threshold
    'convergence': 'uniform(0,5)',                                          # convergence (num presyn targeting postsyn) is uniformly distributed between 1 and 10
    'synMech': 'exc'}
# Excitory to middle and output
netParams.connParams['E->EIOut'] = {
    'preConds': {'cellType': 'E'},
    'postConds': {'cellType': ['E', 'I', 'Out']},
	'weight': cfg.exc_weight,
    'probability': 'max_prob_const*exp(-prob_dist_factor*dist_3D/probLengthConst)', # probability of connection
    'delay': 'dist_3D/propVelocity',                                        # delay min=0.2, mean=13.0, var = 1.4
    'threshold': 10,                                                        # threshold
    'convergence': 'uniform(0,5)',                                          # convergence (num presyn targeting postsyn) is uniformly distributed between 1 and 10
    'synMech': 'exc'}#,
	#'plast': {'mech': 'STDP', 'params': STDPparams}}
# Inhibitory to middle and output
netParams.connParams['I->EIOut'] = {
  'preConds': {'cellType': 'I'},
  'postConds': {'cellType': ['E', 'I', 'Out']},
  'weight': cfg.inh_weight, 													# weight of each connection
  'probability': 'max_prob_const*exp(-prob_dist_factor*dist_3D/probLengthConst)',   # probability of connection
  'delay': 'dist_3D/propVelocity',                                          # transmission delay (ms)
  'threshold': 10,                                                          # threshold
  'convergence': 'uniform(0,5)',                                            # convergence (num presyn targeting postsyn) is uniformly distributed between 1 and 10
  'synMech': 'inh'}#,
  #'plast': {'mech': 'STDP', 'params': STDPparams}}                                                         # synaptic mechanism

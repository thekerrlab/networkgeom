from netpyne import specs, sim
try:
	from __main__ import *  # import SimConfig object with params from parent module
except:
	from config import *  # if no simConfig in parent module, import directly from tut8_cfg module
import math

# Network parameters - object of class NetParams to store the network parameters
netParams = specs.NetParams()

## Constants/Variables
# Size of network and length constant for connection probability
netParams.sizeX = cfg.horizontal_lengths # x-dimension (horizontal length) size in um
netParams.sizeY = cfg.vertical_length # y-dimension (vertical height or cortical depth) size in um
netParams.sizeZ = cfg.horizontal_lengths # z-dimension (horizontal length) size in um
xRange = [0,netParams.sizeX]
yRange = [0,netParams.sizeY]
zRange = [0,netParams.sizeZ]
#netParams.maxDist = math.sqrt(pow(xRange[1]-xRange[0],2)+pow(yRange[1]-yRange[0],2) +pow(zRange[1]-zRange[0],2))
netParams.propVelocity = cfg.propagation_velocity	# propagation velocity (um/ms)
netParams.probLengthConst = cfg.prob_length_const 	# length constant for conn probability (um)
# Constants for Weight and probability
netParams.max_prob_const = cfg.max_conn_probability
netParams.prob_dist_factor = cfg.exp_dist_factor_prob

## Population parameters
netParams.popParams['PYR_Izhi_excit'] = {'cellModel': 'Izhi', 'cellType': 'E', 'xRange': xRange, 'yRange': yRange, 'zRange': zRange, 'numCells': 50}
netParams.popParams['PYR_Izhi_inhib'] = {'cellModel': 'Izhi', 'cellType': 'I', 'xRange': xRange, 'yRange': yRange, 'zRange': zRange, 'numCells': 50}

## Cell property rules
# Excitory cells (Izhi)
cellRule = {'conds': {'cellType': 'E', 'cellModel': 'Izhi'}, 'secs': {}}
cellRule['secs']['soma'] = {'geom': {}, 'pointps': {}}    # soma properties
cellRule['secs']['soma']['geom'] = {'diam': 10, 'L': 10, 'cm': 31.831} # soma geometry
cellRule['secs']['soma']['pointps']['Izhi'] = {'mod':'Izhi2007b',
    'C':1, 'k':0.7, 'vr':-60, 'vt':-40, 'vpeak':35, 'a':0.03, 'b':-2, 'c':-50, 'd':100, 'celltype':1}
netParams.cellParams['PYR_Izhi_excit'] = cellRule

# Inhibitory cells (Izhi)
cellRule = {'conds': {'cellType': 'I', 'cellModel': 'Izhi'}, 'secs': {}}
cellRule['secs']['soma'] = {'geom': {}, 'pointps': {}}    # soma properties
cellRule['secs']['soma']['geom'] = {'diam': 10, 'L': 10, 'cm': 31.831} # soma geometry
cellRule['secs']['soma']['pointps']['Izhi'] = {'mod':'Izhi2007b',
    'C':1, 'k':0.7, 'vr':-60, 'vt':-40, 'vpeak':35, 'a':0.03, 'b':-2, 'c':-50, 'd':100, 'celltype':1}
netParams.cellParams['PYR_Izhi_inhib'] = cellRule												# add dict to list of cell params

## Synaptic mechanism parameters
# netParams.synMechParams['AMPA'] = {'mod': 'ExpSyn', 'tau': 0.1, 'e': 0}
netParams.synMechParams['bkg'] = {'mod': 'Exp2Syn', 'tau1': 0.8, 'tau2': 5.3, 'e': 0}  # NMDA/AMPA synaptic mechanism
netParams.synMechParams['exc'] = {'mod': 'Exp2Syn', 'tau1': 0.8, 'tau2': 5.3, 'e': 0}  # NMDA/AMPA synaptic mechanism
netParams.synMechParams['inh'] = {'mod': 'Exp2Syn', 'tau1': 0.6, 'tau2': 8.5, 'e': -75}  # GABA synaptic mechanism

# Stimulation parameters
netParams.stimSourceParams['bkg'] = {'type': 'NetStim', 'rate': 150, 'noise': 0.5}
netParams.stimTargetParams['bkg->all'] = {'source': 'bkg', 'conds': {'cellType': ['E','I']},
                                        'weight': 0.001, 'delay': 'max(1, normal(5,2))', 'synMech': 'bkg'}

## Cell connectivity rules
# Excitory to all
netParams.connParams['E->all'] = {
    'preConds': {'cellType': 'E'},
    'postConds': {'cellType': ['E', 'I']},
	'weight': 0.1*cfg.weight,
    'probability': 'max_prob_const*exp(-prob_dist_factor*dist_3D/probLengthConst)', # probability of connection
    'delay': 'dist_3D/propVelocity',                                        # delay min=0.2, mean=13.0, var = 1.4
    'threshold': 10,                                                        # threshold
    'convergence': 'uniform(0,5)',                                          # convergence (num presyn targeting postsyn) is uniformly distributed between 1 and 10
    'synMech': 'exc'}
# Inhibitory to all
netParams.connParams['I->all'] = {
  'preConds': {'cellType': 'I'},
  'postConds': {'cellType': ['E','I']},
  'weight': 1*cfg.weight, 													# weight of each connection
  'probability': 'max_prob_const*exp(-prob_dist_factor*dist_3D/probLengthConst)',   # probability of connection
  'delay': 'dist_3D/propVelocity',                                          # transmission delay (ms)
  'threshold': 10,                                                          # threshold
  'convergence': 'uniform(0,5)',                                            # convergence (num presyn targeting postsyn) is uniformly distributed between 1 and 10
  'synMech': 'inh'}                                                         # synaptic mechanism

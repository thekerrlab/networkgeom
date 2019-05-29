from netpyne import specs

# Configuration parameters - object of class SimConfig to store the simulation configuration
cfg = specs.SimConfig()

# Geometric configuration parameters
cfg.input_horiz_len = 200            # X and Z square dimensions
cfg.input_vert_loc = 0              # Y - the vertical dimension
cfg.middle_horiz_len = 200          # X and Z square dimensions
cfg.middle_vert_loc = 100           # Y - the vertical dimension
cfg.output_horiz_len = 200           # X and Z square dimensions
cfg.output_vert_loc = 200           # Y - the vertical dimension

# Visibility Area around sprite
cfg.visibleSize = 7 # square area of this width and height

# Size of populations
cfg.input_pop_size = cfg.visibleSize*cfg.visibleSize
cfg.middle_pop_size = 28*28
#cfg.middle_exc_pop_size = 28*28#round(28*28/2)
#cfg.middle_inhib_pop_size = 0#round(28*28/2)
cfg.output_pop_size = 9

# Connection and stimulation weights
cfg.backgroundStimWeight = 0.01      # stimulation weight of the background input
cfg.input_weight = 0.01              # Weight of input to middle connections
cfg.middle_exc_weight = 0.00075        # Weight of excitory connections
cfg.middle_inh_weight = 1.8*cfg.middle_exc_weight  # Weight of inhibitory connections
cfg.middle_exc_weight_var = 0.005*cfg.middle_exc_weight
cfg.middle_inh_weight_var = 0.005*cfg.middle_inh_weight

#### Configuration options
##################################################################
cfg.uniformInhibitionWeight = True      # If true, all inhibitory connections are equally weighted
##################################################################
cfg.inputSynapseBalance = True          # heterosynaptic balancing
cfg.balanceExcitatoryOnly = True        # inhibitatory neurons ignored if True, assumes rewarded STDP only on excitatory
cfg.apply_leftovers = True              # Apply < 0 weights to next epoch ensuring net input synaptic activity
##################################################################
cfg.outputFrequencyTargeting = True
cfg.outputCellFrequencyTarget = 1.0     # Hertz (for each output cell)
cfg.outputCellTargetDelta = 0.0001      # Same as foraging paper
##################################################################
cfg.outputBalancing = True              # Output balancing method (modify STDP reward), assumes all->all conns M->O
cfg.minimum_output_balance_ratio = 0.5  # If set to 0 it is possible to get /0 errors
##################################################################
cfg.randomMovementChange = 0.01         # set to 0 to turn off
##################################################################
cfg.softThresholding = 1               # 1 for on, 0 for off
cfg.softThreshold = 10*cfg.middle_exc_weight # Take care that if this is too low, all weights above the threshold are cut
##################################################################

# STDP
cfg.stdp_reward = 1
cfg.stdp_punish = -0.1

# Number of stimulations (equates to number of moves in the simulation)
cfg.numberOfEpochs = 100000
# Background delay between stims
cfg.epochPeriod = 300 # ms

# Number of connections between each input cell and middle layer cell
cfg.fan_in = 9

# Some names set in the conifg space to maintain consistency between run and network
cfg.excitatory_connection_name = 'exc'
cfg.inhibitory_connection_name = 'inh'

# Other variables
#cfg.max_conn_probability = 0.05      # Maximum probability of a connection (when dist = 0)
cfg.exp_dist_factor_prob = 2.0      # Amplifies the distance dependence
cfg.prob_length_const = 150.0       # length at which probability = exp_dist_factor_prob*max_conn_probability/e
cfg.propagation_velocity = 100.0    # propagation velocity (um/ms)

# Simulation parameters
cfg.duration = cfg.epochPeriod*cfg.numberOfEpochs   # Duration of the simulation, in ms
cfg.dt = 0.5                     # Internal integration timestep to use
cfg.seeds = {'conn': 1, 'stim': 1, 'loc': 1} # Seeds for randomizers (connectivity, input stimulation and cell locations)
cfg.createNEURONObj = True        # create HOC objects when instantiating network
cfg.createPyStruct = True         # create Python structure (simulator-independent) when instantiating network
cfg.timing = True                 # show timing  and save to file
cfg.verbose = False               # show detailed messages
cfg.printPopAvgRates = True       # Print some additional info

# Custom verbose
cfg.custom_verbose = False

# Recording
# cfg.recordCells = [0]  # list of cells to record from
# cfg.recordTraces = {'V':{'sec':'soma','loc':0.5,'var':'v'},
#                     'u':{'sec':'soma', 'pointp':'Izhi', 'var':'u'},
#                     'I':{'sec':'soma', 'pointp':'Izhi', 'var':'i'},
#                     'bkg': {'sec':'soma', 'loc':0.5, 'synMech':'bkg', 'var':'i'},
#                     'exc': {'sec':'soma', 'loc':0.5, 'synMech':'exc', 'var':'i'},
#                     'inh': {'sec':'soma', 'loc':0.5, 'synMech':'inh', 'var':'i'},
#                     }
cfg.recordStim = True  # record spikes of cell stims
cfg.recordStep = cfg.dt # Step size in ms to save data (eg. V traces, LFP, etc)

# Saving
cfg.filename = 'networkgeom'  # Set file output name
#cfg.saveFileStep = 1000       # step size in ms to save data to disk
cfg.savePickle = False        # Whether or not to write spikes etc. to a .mat file
cfg.saveJson = False          # Whether or not to write spikes etc. to a .mat file
cfg.saveMat = False           # Whether or not to write spikes etc. to a .mat file
cfg.saveTxt = False           # save spikes and conn to txt file
cfg.saveDpk = False           # save to a .dpk pickled file

# Custom saving
cfg.saveCsvFiles = False
cfg.saveMatFile = True
cfg.mat_file_dir = 'matfiles'
cfg.mat_filename = 'epoch_coretest_1.mat'

# Analysis and plotting
cfg.analysis['plotRaster'] = {'orderBy': 'y', 'orderInverse': True, 'syncLines': False}
# cfg.analysis['plotTraces'] = {'include': cfg.recordCells} # plot recorded traces for this list of cells
# cfg.analysis['plotRatePSD'] =  {'include': ['allCells', 'Input', 'Middle', 'Output'], 'smooth': 10}
# cfg.analysis['plot2Dnet'] = True
# cfg.analysis['plotConn'] = True

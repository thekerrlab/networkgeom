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

# Size of populations
cfg.input_pop_size = 100
cfg.middle_exc_pop_size = 100
cfg.middle_inhib_pop_size = 100
cfg.output_pop_size = 9

# Connection Weights
cfg.input_weight = 0.1              # Weight of input to middle connections
cfg.exc_weight = 0.01               # Weight of excitory connections
cfg.inh_weight = 0.1                # Weight of inhibitory connections

# Background stimulation
cfg.backgroundStimWeight = 0.01     # stimulation weight of the background input

# Background delay between stims
cfg.backgroundStimDelayPeriod = 100
# Number of stimulations (equates to number of moves in the simulation)
cfg.backgroundStimNumber = 20

# Other variables
cfg.max_conn_probability = 0.1      # Maximum probability of a connection (when dist = 0)
cfg.exp_dist_factor_prob = 2.0      # Amplifies the distance dependence
cfg.prob_length_const = 150.0       # length at which probability = exp_dist_factor_prob*max_conn_probability/e
cfg.propagation_velocity = 100.0    # propagation velocity (um/ms)

# Simulation parameters
cfg.duration = cfg.backgroundStimDelayPeriod*cfg.backgroundStimNumber   # Duration of the simulation, in ms
cfg.dt = 0.025                    # Internal integration timestep to use
cfg.seeds = {'conn': 1, 'stim': 1, 'loc': 1} # Seeds for randomizers (connectivity, input stimulation and cell locations)
cfg.createNEURONObj = True        # create HOC objects when instantiating network
cfg.createPyStruct = True         # create Python structure (simulator-independent) when instantiating network
cfg.timing = True                 # show timing  and save to file
cfg.verbose = False               # show detailed messages
cfg.printPopAvgRates = True       # Print some additional info

# Recording
cfg.recordCells = [0]  # list of cells to record from
cfg.recordTraces = {'V':{'sec':'soma','loc':0.5,'var':'v'},
                    'u':{'sec':'soma', 'pointp':'Izhi', 'var':'u'},
                    'I':{'sec':'soma', 'pointp':'Izhi', 'var':'i'},
                    'bkg': {'sec':'soma', 'loc':0.5, 'synMech':'bkg', 'var':'i'},
                    'exc': {'sec':'soma', 'loc':0.5, 'synMech':'exc', 'var':'i'},
                    'inh': {'sec':'soma', 'loc':0.5, 'synMech':'inh', 'var':'i'},
                    }
cfg.recordStim = True  # record spikes of cell stims
cfg.recordStep = 0.025 # Step size in ms to save data (eg. V traces, LFP, etc)

# Saving
cfg.filename = 'networkgeom'  # Set file output name
cfg.saveFileStep = 1000       # step size in ms to save data to disk
cfg.savePickle = False        # Whether or not to write spikes etc. to a .mat file
cfg.saveJson = False          # Whether or not to write spikes etc. to a .mat file
cfg.saveMat = False           # Whether or not to write spikes etc. to a .mat file
cfg.saveTxt = False           # save spikes and conn to txt file
cfg.saveDpk = False           # save to a .dpk pickled file


# Analysis and plotting
cfg.analysis['plotRaster'] = {'orderBy': 'y', 'orderInverse': True, 'syncLines': False}
cfg.analysis['plotTraces'] = {'include': cfg.recordCells} # plot recorded traces for this list of cells
cfg.analysis['plotRatePSD'] =  {'include': ['allCells', 'Izhi_excit', 'Izhi_inhib'], 'smooth': 10}
cfg.analysis['plot2Dnet'] = True
cfg.analysis['plotConn'] = True

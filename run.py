from netpyne import sim

'''
netParams is a dict containing a set of network parameters using a standardized structure
simConfig is a dict containing a set of simulation configurations using a standardized structure
'''

# read cfg and netParams from command line arguments if available; otherwise use default
simConfig, netParams = sim.readCmdLineArgs(simConfigDefault='config.py', netParamsDefault='network.py')

# Create network and run simulation
sim.createSimulateAnalyze(netParams=netParams, simConfig=simConfig)

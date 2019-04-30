from netpyne import sim
from Forage import *

'''
netParams is a dict containing a set of network parameters using a standardized structure
simConfig is a dict containing a set of simulation configurations using a standardized structure
'''

# Create forage object
forage = Forage(10,10,0.1)
# Get the occupied cells from the forage instance (already in scope)
forageCellList = forage.getOccupiedGridList()
print("Initial cells to stimulate:" + str(forageCellList))

# read cfg and netParams from command line arguments if available; otherwise use default
simConfig, netParams = sim.readCmdLineArgs(simConfigDefault='config.py', netParamsDefault='network.py')

# Create network and run simulation
#sim.createSimulateAnalyze(netParams=netParams, simConfig=simConfig)
sim.create(simConfig = simConfig, netParams = netParams)

# Initialisation
sim.updateInterval = cfg.backgroundStimDelayPeriod
sim.allWeights = [] # Store weight changes here

numberCells = cfg.input_pop_size + cfg.middle_exc_pop_size \
                + cfg.middle_inhib_pop_size + cfg.output_pop_size
outputCellSize = cfg.output_pop_size
indexOfFirstOutputCell = numberCells - outputCellSize
indexOfFirstUnprocessedSpike = 0

# Update function
# t = time in simulation
def update(t):
    global indexOfFirstUnprocessedSpike
    global forageCellList
    # Extract output cell activity to get direction
    spikingCells = sim.simData['spkid']
    spikingOutputCells = [spikingCell for spikingCell in spikingCells if spikingCell >= indexOfFirstOutputCell]
    # Only move player if there are unprocessed spikes, otherwise leave critic = 0
    critic = 0
    print("Output spikes thus far: " + str(len(spikingOutputCells)))
    if len(spikingOutputCells) > indexOfFirstUnprocessedSpike:
        nextFirstIdx = len(spikingOutputCells) # Hold this variables temporarily
        # Strip to look at only unseen spikes
        spikingOutputCells = spikingOutputCells[indexOfFirstUnprocessedSpike:]
        indexOfFirstUnprocessedSpike = nextFirstIdx
        print("Cells with new spikes: " + str(spikingOutputCells))
        # Find most active output cell
        mostActiveOutputCell = max(set(spikingOutputCells), key = spikingOutputCells.count)
        # Move the sprite and determine critic value
        direction = mostActiveOutputCell - indexOfFirstOutputCell + 1 # range of 1-9
        critic = forage.movePlayer(direction)
        print("Direction code: " + str(direction))

    # Reward or punish depending on critic
    for cell in sim.net.cells:
        for conn in cell.conns:
            STDPmech = conn.get('hSTDP')  # check if has STDP mechanism
            if STDPmech:   # run stdp.mod method to update syn weights based on RLprint cell.gid
                STDPmech.reward_punish(float(critic))

    # store weight changes to analyse later
    sim.allWeights.append([]) # Save this time
    for cell in sim.net.cells:
        for conn in cell.conns:
            if 'hSTDP' in conn:
                sim.allWeights[-1].append(float(conn['hObj'].weight[0])) # save weight only for STDP conns

    # Send a new burst for new cells
    '''
    inputStims = [sim.net.cells[forageCellList[i]].stims[0] for i in range(len(forageCellList))]
    #print(inputStims)
    for i in forageCellList:
        #print(sim.net.cells[i].stims)
        sim.net.cells[i].stims.clear()
        #print(sim.net.cells[i].stims)
    forageCellList = forage.getOccupiedGridList()
    idx = 0
    for i in forageCellList:
        #print(sim.net.cells[i].stims)
        sim.net.cells[i].stims.append(inputStims[idx])
        idx += 1
        #print(sim.net.cells[i].stims)
    input()
    '''
    '''
    #print(sim.simData.stims)
    #print(forageCellList)
    #input()
    inputStim = sim.simData.stims[list(sim.simData.stims)[forageCellList[0]]]
    # Clear current stims
    for cellNum in forageCellList:
        sim.simData.stims[list(sim.simData.stims)[cellNum]] = {}
    # Get new list
    forageCellList = forage.getOccupiedGridList()
    # Add new stims
    for cellNum in forageCellList:
        sim.simData.stims[list(sim.simData.stims)[cellNum]][list(inputStim.keys())[0]] = inputStim['Input']
    #print(sim.simData.stims)
    #print(forageCellList)
    #input()
    '''

    forageCellList = forage.getOccupiedGridList()
    #sim.net.modifyStims({'conds': {'label': 'Input->input'}, 'cellConds': {'cellType': 'In'}, 'weight': cfg.backgroundStimWeight})
    for i in range(cfg.input_pop_size):
        for conn in sim.net.cells[i].conns:
            conn['source'] = 'Input'
            sim.net.cells[i].tags['turnOnFlag'] = 0
        if i in forageCellList:
            sim.net.cells[i].tags['turnOnFlag'] = 1
    sim.net.modifyStims({'conds': {'source': 'Input'}, 'cellConds': {'cellType': 'In', 'turnOnFlag': 1}, 'weight': cfg.backgroundStimWeight})
    sim.net.modifyStims({'conds': {'source': 'Input'}, 'cellConds': {'cellType': 'In', 'turnOnFlag': 0}, 'weight': 0})

    '''
    for cellNum in range(cfg.input_pop_size):
        if cellNum in forageCellList:
            sim.net.modifyStims({'conds': {'label': 'Input->input'}, 'cellConds': {'cellType': ['In']]}, 'weight': cfg.backgroundStimWeight})
        else:
            sim.net.modifyStims({'conds': {'label': 'Input->input'}, 'cellConds': {'gid': cellNum}, 'weight': 0})
    '''

    print("Cells to stimulate:" + str(forageCellList))

# Run simulation
sim.runSimWithIntervalFunc(sim.updateInterval, update)   # run parallel Neuron simulation
sim.gatherData()                                                # gather spiking data and cell info from each node
sim.saveData()                                                  # save params, cell info and sim output to file (pickle,mat,txt,etc)
sim.analysis.plotData()                                         # plot spike raster

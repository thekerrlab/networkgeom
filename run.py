from netpyne import sim
from Forage import *
from utility import *
import random
import statistics

'''
netParams is a dict containing a set of network parameters using a standardized structure
simConfig is a dict containing a set of simulation configurations using a standardized structure
'''

# read cfg and netParams from command line arguments if available; otherwise use default
simConfig, netParams = sim.readCmdLineArgs(simConfigDefault='config.py', netParamsDefault='network.py')

# Create network and run simulation
#sim.createSimulateAnalyze(netParams=netParams, simConfig=simConfig)
sim.create(simConfig = simConfig, netParams = netParams)
'''sim.initialize(netParams, simConfig)  # create network object and set cfg and net params
pops = sim.net.createPops()                  # instantiate network populations
cells = sim.net.createCells()                 # instantiate network cells based on defined populations
conns = sim.net.connectCells()                # create connections between cells based on params
stims = sim.net.addStims()                    # add external stimulation to cells (IClamps etc)
rxd = sim.net.addRxD()                    # add reaction-diffusion (RxD)
simData = sim.setupRecording()             # setup variables to record for each cell (spikes, V traces, etc)
'''
# Initialisation
sim.updateInterval = cfg.backgroundStimDelayPeriod
sim.allWeights = [] # Store weight changes here
sim.allWeightsStats = {} # Store stats about weights here
sim.performances = [] # Store post-epoch performance here

# Initialise Forage environment
# Create forage object
forage = Forage(49,49,0.1)
forage.printField()
# Get the occupied cells from the forage instance (already in scope)
forageCellList = forage.getVisibleAreaSubGridList(cfg.visibleSize,cfg.visibleSize)
print("Initial cells to stimulate:" + str(forageCellList))

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
    # Print Progress:
    progress = t/cfg.duration
    printProgress(progress)
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
        #mostActiveOutputCell = max(set(spikingOutputCells), key = spikingOutputCells.count)
        mostActiveOutputCells = modesFromList(spikingOutputCells)
        mostActiveOutputCell = mostActiveOutputCells[random.randint(0,len(mostActiveOutputCells)-1)]
        # Determine direction ot move
        direction = mostActiveOutputCell - indexOfFirstOutputCell + 1 # range of 1-9
    else:
        # Choose a random direction (1-8 maps to 1-4, 6-9)
        direction = random.randint(1, 8)
        if direction >= 5: # map 5-8 to 6-9
            direction += 1
    # Move the sprite and determine critic value
    collectedFood = forage.movePlayer(direction)
    if collectedFood == 1:
        critic = 1
    else:
        critic = -0.1
    print("Direction code: " + str(direction))
    print("Critic: " + str(critic))

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
    '''
    for cellNum in range(cfg.input_pop_size):
        if cellNum in forageCellList:
            sim.net.modifyStims({'conds': {'label': 'Input->input'}, 'cellConds': {'cellType': ['In']]}, 'weight': cfg.backgroundStimWeight})
        else:
            sim.net.modifyStims({'conds': {'label': 'Input->input'}, 'cellConds': {'gid': cellNum}, 'weight': 0})
    '''

    #forageCellList = forage.getOccupiedGridList()
    #sim.net.modifyStims({'conds': {'label': 'Input->input'}, 'cellConds': {'cellType': 'In'}, 'weight': cfg.backgroundStimWeight})
    forageCellList = forage.getVisibleAreaSubGridList(cfg.visibleSize,cfg.visibleSize)
    for i in range(cfg.input_pop_size):
        for conn in sim.net.cells[i].conns:
            conn['source'] = 'Input'
            sim.net.cells[i].tags['turnOnFlag'] = 0
        if i in forageCellList:
            sim.net.cells[i].tags['turnOnFlag'] = 1
    sim.net.modifyStims({'conds': {'source': 'Input'}, 'cellConds': {'cellType': 'In', 'turnOnFlag': 1}, 'weight': cfg.backgroundStimWeight})
    sim.net.modifyStims({'conds': {'source': 'Input'}, 'cellConds': {'cellType': 'In', 'turnOnFlag': 0}, 'weight': 0})
    print("Cells to stimulate next: " + str(forageCellList))

    # Performance and analysis
    forage.printPerformance()
    sim.performances.append(forage.getGatheringRate())
    print("Total number of STDP connections: " + str(len(sim.allWeights[0])))
    print("Initial weights of STDP connections:")
    printStats(sim.allWeights[0])
    if len(sim.allWeights) > 1:
        print("Previous weights of STDP connections:")
        printStats(sim.allWeights[-2])
    print("Final weights of STDP connections:")
    printStats(sim.allWeights[-1])
    stats = getStats(sim.allWeights[-1])
    for key in stats.keys():
        if sim.allWeightsStats.get(key) == None:
            sim.allWeightsStats[key] = []
        sim.allWeightsStats[key].append(stats[key])

# Run simulation
sim.runSimWithIntervalFunc(sim.updateInterval, update)   # run parallel Neuron simulation
sim.gatherData()                                                # gather spiking data and cell info from each node
sim.saveData()                                                  # save params, cell info and sim output to file (pickle,mat,txt,etc)
sim.analysis.plotData()                                         # plot spike raster

if cfg.saveCsvFiles:
    saveMatrixInFile(sim.performances, 'csvfiles/performances.csv')
    saveMatrixInFile(sim.allWeightsStats['sum'], 'csvfiles/weights_sum.csv')
    saveMatrixInFile(sim.allWeightsStats['mean'], 'csvfiles/weights_mean.csv')
    saveMatrixInFile(sim.allWeightsStats['var'], 'csvfiles/weights_var.csv')
    saveMatrixInFile(sim.allWeights[0], 'csvfiles/weights_init.csv')
    saveMatrixInFile(sim.allWeights[-1], 'csvfiles/weights_final.csv')

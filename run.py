from netpyne import sim
from Forage import *
from utility import *
import random
import statistics
import numpy

'''
netParams is a dict containing a set of network parameters using a standardized structure
simConfig is a dict containing a set of simulation configurations using a standardized structure
'''

# read cfg and netParams from command line arguments if available; otherwise use default
simConfig, netParams = sim.readCmdLineArgs(simConfigDefault='config.py', netParamsDefault='network.py')

# Create network and run simulation
sim.create(simConfig = simConfig, netParams = netParams)

# Initialisation
sim.updateInterval = cfg.epochPeriod
sim.excStdpWeights = [] # Store weight changes here
sim.inhWeights = [] # Store inhibitory neuron weights here
sim.excStdpWeightsStats = {} # Store stats about weights here
sim.performances = [] # Store post-epoch performance here
sim.outputFrequencies = [] # Store output cell firing frequencies here

# Initialise Forage environment
# Create forage object
forage = Forage(49,49,0.1)
forage.printField()
# Get the occupied cells from the forage instance (already in scope)
forageCellList = forage.getVisibleAreaSubGridList(cfg.visibleSize,cfg.visibleSize)
print("Initial cells to stimulate:" + str(forageCellList))

#numberCells = cfg.input_pop_size + cfg.middle_exc_pop_size \
                #+ cfg.middle_inhib_pop_size + cfg.output_pop_size
numberCells = cfg.input_pop_size + cfg.middle_pop_size + cfg.output_pop_size

outputCellSize = cfg.output_pop_size
indexOfFirstOutputCell = numberCells - outputCellSize
indexOfFirstUnprocessedSpike = 0

# Frequency recording over all epochs
outputCellFrequencies = [0]*cfg.output_pop_size     # List of output cell frequencies
outputCellNumSpikes = [0]*cfg.output_pop_size       # Helper for frequency

if cfg.outputFrequencyTargeting:
    outputCellExcSynapseInput = [0]*cfg.output_pop_size    # sum of synaptic input to each output cell
    outputCellTargetExcSynapseInput = [0]*cfg.output_pop_size # Gradually shifting target synaptic input
    outputCells = sim.net.cells[-cfg.output_pop_size:]
    for cellNum in range(cfg.output_pop_size):
        cell = outputCells[cellNum]
        for conn in cell.conns:
            # Only look at the excitatory connections
            if conn.synMech == cfg.excitatory_connection_name:
                outputCellExcSynapseInput[cellNum] += conn['weight']
                outputCellTargetExcSynapseInput[cellNum] += conn['weight']
    print("Initial Output Neuron Synapse Input: " + str(outputCellExcSynapseInput))

if cfg.randomMovementChange > 0:
    numberOfRandomMovementsCounter = 0

# Define leftover_synaptic_inputs as the amount of synaptic input that is nullified by all
# max(0, weight) operations for a cell. It is subtracted equally amongst all connections
# on the next epoch and re-set each epoch
# This ensures that total input synaptic balance is maintained
if cfg.inputSynapseBalance and cfg.apply_leftovers:
    leftover_synaptic_inputs = [0]*len(sim.net.cells)

if cfg.outputBalancing:
    middleCellsInitialOutputWeightSum = [0]*cfg.middle_pop_size
    for middleCellNum in range(cfg.middle_pop_size):
        for cell in sim.net.cells[-cfg.output_pop_size:]:
            middleCellsInitialOutputWeightSum[middleCellNum] += cell.conns[middleCellNum].weight

# Update function
# t = time in simulation
def update(t):
    # global variables so that update can see them (alternatively make them part of sim)
    global indexOfFirstUnprocessedSpike
    global forageCellList
    global outputCellFrequencies
    global outputCellNumSpikes
    global outputCellExcSynapseInput
    global outputCellTargetExcSynapseInput
    global numberOfRandomMovementsCounter
    global leftover_synaptic_inputs
    # Update
    print("\nEPOCH UPDATE (t=)" + str(t) + "):")
    # Print Progress:
    progress = t/cfg.duration
    printProgress(progress)
    # Extract output cell activity to get direction
    spikingCells = sim.simData['spkid']
    spikingOutputCells = [spikingCell for spikingCell in spikingCells if spikingCell >= indexOfFirstOutputCell]
    # Only move player if there are unprocessed spikes, otherwise leave critic = 0
    print("\tNumber of output spikes thus far: " + str(len(spikingOutputCells)))
    if len(spikingOutputCells) > indexOfFirstUnprocessedSpike:
        nextFirstIdx = len(spikingOutputCells) # Hold this variables temporarily
        # Strip to look at only unseen spikes
        spikingOutputCells = spikingOutputCells[indexOfFirstUnprocessedSpike:]
        print("\tNumber of new spikes this epoch: " + str(len(spikingOutputCells)))
        indexOfFirstUnprocessedSpike = nextFirstIdx
        print("\tCells with new spikes: " + str(spikingOutputCells))
        # Record num new spikes of output cell
        for cellNum in range(cfg.output_pop_size):
            cell_index = indexOfFirstOutputCell + cellNum
            outputCellNumSpikes[cellNum] += len([spike for spike in spikingOutputCells if spike == cell_index])
        # Find most active output cell
        mostActiveOutputCells = modesFromList(spikingOutputCells)
        mostActiveOutputCell = mostActiveOutputCells[random.randint(0,len(mostActiveOutputCells)-1)]
        # Determine direction ot move
        direction = mostActiveOutputCell - indexOfFirstOutputCell + 1 # range of 1-9
        # Chance for random direction:
        if random.uniform(0, 1) < cfg.randomMovementChange:
            print("\tRandom movement occurred! (probability is 1 in {})".format(1/cfg.randomMovementChange))
            numberOfRandomMovementsCounter += 1
            direction = random.randint(1, 8)
            if direction >= 5: # map 5-8 to 6-9
                direction += 1
    else:
        # Choose a random direction (1-8 maps to 1-4, 6-9)
        direction = random.randint(1, 8)
        if direction >= 5: # map 5-8 to 6-9
            direction += 1
    if cfg.randomMovementChange > 0:
        print("\tNumber of random movements so far = {}".format(numberOfRandomMovementsCounter))
    # Redetermine output cell frequency
    for cellNum in range(cfg.output_pop_size):
        outputCellFrequencies[cellNum] = outputCellNumSpikes[cellNum]/(t/1000.0)
        if cfg.outputFrequencyTargeting:
            if (outputCellFrequencies[cellNum] < cfg.outputCellFrequencyTarget):
                adjustment = (1 + cfg.outputCellTargetDelta)
            else:
                adjustment = (1 - cfg.outputCellTargetDelta)
            outputCellTargetExcSynapseInput[cellNum] *= adjustment
    # Move the sprite and determine critic value
    collectedFood = forage.movePlayer(direction)
    if collectedFood == 1:
        critic = cfg.stdp_reward
    else:
        critic = cfg.stdp_punish
    print("\tDirection code: " + str(direction))
    print("\tCritic: " + str(critic))
    # Reward or punish depending on critic
    total_change_to_cells = 0
    total_weight_change = 0
    for cellNum in range(len(sim.net.cells)):
        cell = sim.net.cells[cellNum]
        if cfg.inputSynapseBalance:
            # Extract the connections we are interested in:
            if cfg.balanceExcitatoryOnly:
                connections = [conn for conn in cell.conns if conn.synMech == cfg.excitatory_connection_name]
            else:
                connections = cell.conns
            number_of_connections = len(connections)
            # array holding accumulative adjustments for each connection
            conn_adjustments = numpy.array([0.0] * number_of_connections)
        else:
            # Extract the connections we are interested in:
            connections = cell.conns
            number_of_connections = len(connections)
        # Loop through the connections we are interested in
        for connNum in range(number_of_connections):
            conn = connections[connNum]
            # check if has STDP mechanism, run stdp.mod method to update syn weights based on RLprint cell.gid
            STDPmech = conn.get('hSTDP')
            if STDPmech:
                # record weight before
                if cfg.inputSynapseBalance:
                    weight_before = float(conn['hObj'].weight[0])
                # Determine output balance ratio
                if cfg.outputBalancing:
                    precell_index_in_middle = conn.preGid - cfg.input_pop_size
                    output_weight_sum = 0.0
                    for cell in sim.net.cells[-cfg.output_pop_size:]:
                        output_weight_sum += float(cell.conns[precell_index_in_middle]['hObj'].weight[0])
                    output_balance_ratio = output_weight_sum/middleCellsInitialOutputWeightSum[precell_index_in_middle]
                    output_balance_ratio = max(cfg.minimum_output_balance_ratio, output_balance_ratio)
                else:
                    output_balance_ratio = 1.0
                # Rewarded STDP
                STDPmech.reward_punish(float(critic/output_balance_ratio))
                # find weight after
                if cfg.inputSynapseBalance:
                    weight_after = float(conn['hObj'].weight[0])
                    weight_change = weight_after - weight_before
                    total_weight_change += weight_change
                    # Loop through other (input) synapses and reduce their weight
                    deltaW = weight_change/(number_of_connections-1)
                    # Adjust whole array:
                    conn_adjustments -= deltaW
                    # undo adjustment for the changed connection:
                    conn_adjustments[connNum] += deltaW
        if cfg.apply_leftovers:
            if leftover_synaptic_inputs[cellNum] > 0 and number_of_connections > 0:
                # Leftovers
                deltaLeftover = leftover_synaptic_inputs[cellNum]/number_of_connections
                conn_adjustments -= deltaLeftover
            leftover_synaptic_inputs[cellNum] = 0
        if cfg.inputSynapseBalance:
            # Change every connection
            if sum(conn_adjustments) != 0:
                #print("\ttotal adjustment to conn = {:.3e}".format(sum(conn_adjustments)))
                total_change_to_cells += sum(conn_adjustments)
            for connNum in range(number_of_connections):
                conn = connections[connNum]
                # Don't allow weight to drop below 0
                conn['hObj'].weight[0] += conn_adjustments[connNum]
                if cfg.apply_leftovers:
                    leftover_synaptic_inputs[cellNum] += max(0, -conn['hObj'].weight[0])
                conn['hObj'].weight[0] = max(0, conn['hObj'].weight[0])
    # After STDP events, adjust weight of all excitatory input synapses
    if cfg.outputFrequencyTargeting:
        outputCells = sim.net.cells[-cfg.output_pop_size:]
        for cellNum in range(cfg.output_pop_size):
            cell = outputCells[cellNum]
            # Calculate scale factor and set next outputCellExcSynapseInput
            scaleFactor = outputCellTargetExcSynapseInput[cellNum]/outputCellExcSynapseInput[cellNum]
            outputCellExcSynapseInput[cellNum] *= scaleFactor
            for conn in cell.conns:
                # Only change the excitatory connections
                if conn.synMech == cfg.excitatory_connection_name:
                    #print("{:.5e}\t".format(conn['hObj'].weight[0]), end="")
                    #conn['hObj'].weight[0] = max(0, conn['hObj'].weight[0] * scaleFactor)
                    conn['hObj'].weight[0] *= scaleFactor
                    #print("{:.5e}\t".format(conn['hObj'].weight[0]), end="")
                    #print("{:.5e}\t".format(scaleFactor), end="")
                    #print(str(conn.get('hSTDP')))
    if cfg.inputSynapseBalance:
        print("\ttotal recorded weight change = {:.3e}".format(total_weight_change))
        print("\ttotal adjustment to other cells = {:.3e}".format(total_change_to_cells))

    # store weight changes to analyse later
    sim.excStdpWeights.append([])
    sim.inhWeights.append([])
    for cell in sim.net.cells:
        for conn in cell.conns:
            if 'hSTDP' in conn and conn.synMech == cfg.excitatory_connection_name:
                sim.excStdpWeights[-1].append(float(conn['hObj'].weight[0]))
            elif conn.synMech == cfg.inhibitory_connection_name:
                sim.inhWeights[-1].append(float(conn['hObj'].weight[0]))

    # Send a new burst for new cells
    forageCellList = forage.getVisibleAreaSubGridList(cfg.visibleSize,cfg.visibleSize)
    for i in range(cfg.input_pop_size):
        for conn in sim.net.cells[i].conns:
            conn['source'] = 'Input'
            sim.net.cells[i].tags['turnOnFlag'] = 0
        if i in forageCellList:
            sim.net.cells[i].tags['turnOnFlag'] = 1
    sim.net.modifyStims({'conds': {'source': 'Input'}, 'cellConds': {'cellType': 'In', 'turnOnFlag': 1}, 'weight': cfg.backgroundStimWeight})
    sim.net.modifyStims({'conds': {'source': 'Input'}, 'cellConds': {'cellType': 'In', 'turnOnFlag': 0}, 'weight': 0})
    print("\tCells to stimulate next: " + str(forageCellList))

    # Performance and analysis
    forage.printPerformance()
    sim.performances.append(forage.getGatheringRate())
    if cfg.custom_verbose:
        print("\tTotal number of STDP connections: " + str(len(sim.excStdpWeights[0])))
        print("\tInitial weights of STDP connections:")
        printStats(sim.excStdpWeights[0])
        if len(sim.excStdpWeights) > 1:
            print("\tPrevious weights of STDP connections:")
            printStats(sim.excStdpWeights[-2])
            print("\tTotal weight change to final = {:.5f}".format(sum(sim.excStdpWeights[-1])-sum(sim.excStdpWeights[-2])))
        print("\tFinal weights of STDP connections:")
        printStats(sim.excStdpWeights[-1])
    stats = getStats(sim.excStdpWeights[-1])
    for key in stats.keys():
        if sim.excStdpWeightsStats.get(key) == None:
            sim.excStdpWeightsStats[key] = []
        sim.excStdpWeightsStats[key].append(stats[key])
    sim.outputFrequencies.append(list(outputCellFrequencies))
    print("\tOutput Population Spiking Frequency:")
    print("\tc1:{:.3f} c2:{:.3f} c3:{:.3f} c4:{:.3f} c5:{:.3f} c6:{:.3f} c7:{:.3f} c8:{:.3f} c9:{:.3f}".format(*outputCellFrequencies))
    printStats(outputCellFrequencies)
    if cfg.outputFrequencyTargeting and cfg.custom_verbose:
        print("\tOutput Population Excitatory Synapse Input:")
        print("\tc1:{:.5f} c2:{:.5f} c3:{:.5f} c4:{:.5f} c5:{:.5f} c6:{:.5f} c7:{:.5f} c8:{:.5f} c9:{:.5f}".format(*outputCellExcSynapseInput))
        print("\tOutput Population Excitatory Synapse Input Target:")
        print("\tc1:{:.5f} c2:{:.5f} c3:{:.5f} c4:{:.5f} c5:{:.5f} c6:{:.5f} c7:{:.5f} c8:{:.5f} c9:{:.5f}".format(*outputCellTargetExcSynapseInput))

# Run simulation
sim.runSimWithIntervalFunc(sim.updateInterval, update)   # run parallel Neuron simulation
sim.gatherData()                                                # gather spiking data and cell info from each node
sim.saveData()                                                  # save params, cell info and sim output to file (pickle,mat,txt,etc)
sim.analysis.plotData()                                         # plot spike raster

if cfg.saveCsvFiles:
    saveMatrixInFile(sim.performances, 'csvfiles/performances.csv', 0)
    saveMatrixInFile(sim.excStdpWeightsStats['sum'], 'csvfiles/weights_sum.csv', 0)
    saveMatrixInFile(sim.excStdpWeightsStats['mean'], 'csvfiles/weights_mean.csv', 0)
    saveMatrixInFile(sim.excStdpWeightsStats['var'], 'csvfiles/weights_var.csv', 0)
    saveMatrixInFile(sim.simData['spkid'], 'csvfiles/spkid.csv', 0)
    saveMatrixInFile(sim.simData['spkt'], 'csvfiles/spkt.csv', 0)
    saveMatrixInFile(sim.excStdpWeights, 'csvfiles/exc_stdp_weights.csv', 1)
    saveMatrixInFile(sim.inhWeights, 'csvfiles/inh_weights.csv', 1)
    saveMatrixInFile(sim.outputFrequencies, 'csvfiles/output_cell_frequencies.csv', 1)
    forage.writePathToCSV('csvfiles/path.csv', 'csvfiles/collected_food.csv', 'csvfiles/final_grid.csv')

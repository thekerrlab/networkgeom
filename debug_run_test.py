from config import *
from network import *
from numbers import Number
from deconstructed_cell_addConn import *

# read cfg and netParams from command line arguments if available; otherwise use default
simConfig, netParams = sim.readCmdLineArgs(simConfigDefault='config.py', netParamsDefault='network.py')
# Create network and run simulation
#sim.createSimulateAnalyze(netParams=netParams, simConfig=simConfig)
#sim.create(simConfig = simConfig, netParams = netParams)
sim.initialize(netParams, simConfig)  # create network object and set cfg and net params
pops = sim.net.createPops()                  # instantiate network populations
cells = sim.net.createCells()                 # instantiate network cells based on defined populations

self = sim.net
# Instantiate network connections based on the connectivity rules defined in params
sim.timing('start', 'connectTime')
if sim.rank==0:
    print('Making connections...')

if sim.nhosts > 1: # Gather tags from all cells
    allCellTags = sim._gatherAllCellTags()
else:
    allCellTags = {cell.gid: cell.tags for cell in self.cells}

allPopTags = {-i: pop.tags for i,pop in enumerate(self.pops.values())}  # gather tags from pops so can connect NetStim pops
if self.params.subConnParams:  # do not create NEURON objs until synapses are distributed based on subConnParams
    origCreateNEURONObj = bool(sim.cfg.createNEURONObj)
    origAddSynMechs = bool(sim.cfg.addSynMechs)
    sim.cfg.createNEURONObj = False
    sim.cfg.addSynMechs = False

gapJunctions = False  # assume no gap junctions by default
for connParamLabel,connParamTemp in self.params.connParams.items():  # for each conn rule or parameter set
    print(connParamLabel)
    print(connParamTemp)
    input()
    connParam = connParamTemp.copy()
    connParam['label'] = connParamLabel
    # find pre and post cells that match conditions
    preCellsTags, postCellsTags = self._findPrePostCellsCondition(allCellTags, connParam['preConds'], connParam['postConds'])
    # if conn function not specified, select based on params
    if 'connFunc' not in connParam:
        if 'probability' in connParam: connParam['connFunc'] = 'probConn'  # probability based func
        elif 'convergence' in connParam: connParam['connFunc'] = 'convConn'  # convergence function
        elif 'divergence' in connParam: connParam['connFunc'] = 'divConn'  # divergence function
        elif 'connList' in connParam: connParam['connFunc'] = 'fromListConn'  # from list function
        else: connParam['connFunc'] = 'fullConn'  # convergence function
    connFunc = getattr(self, connParam['connFunc'])  # get function name from params
    print("\tconnFunc:")
    print(connFunc)
    input()
    # process string-based funcs and call conn function
    if preCellsTags and postCellsTags:
        # initialize randomizer in case used in string-based function (see issue #89 for more details)
        self.rand.Random123(sim.hashStr('conn_'+connParam['connFunc']),
                            sim.hashList(sorted(preCellsTags)+sorted(postCellsTags)),
                            sim.cfg.seeds['conn'])
        input("ran Random123")
        self._connStrToFunc(preCellsTags, postCellsTags, connParam)  # convert strings to functions (for the delay, and probability params)
        input("ran _connStrToFunc")
        ##############
        if sim.cfg.verbose: print('Generating set of probabilistic connections (rule: %s) ...' % (connParam['label']))
        allRands = self.generateRandsPrePost(preCellsTags, postCellsTags)
        # get list of params that have a lambda function
        paramsStrFunc = [param for param in [p+'Func' for p in self.connStringFuncParams] if param in connParam]
        # copy the vars into args immediately and work out which keys are associated with lambda functions only once per method
        funcKeys = {}
        for paramStrFunc in paramsStrFunc:
            connParam[paramStrFunc + 'Args'] = connParam[paramStrFunc + 'Vars'].copy()
            funcKeys[paramStrFunc] = [key for key in connParam[paramStrFunc + 'Vars'] if callable(connParam[paramStrFunc + 'Vars'][key])]
        # probabilistic connections with disynapticBias (deprecated)
        if isinstance(connParam.get('disynapticBias', None), Number):
            allPreGids = sim._gatherAllCellConnPreGids()
            prePreGids = {gid: allPreGids[gid] for gid in preCellsTags}
            postPreGids = {gid: allPreGids[gid] for gid in postCellsTags}
            probMatrix = {(preCellGid,postCellGid): connParam['probabilityFunc'][preCellGid,postCellGid] if 'probabilityFunc' in connParam else connParam['probability']
                                                for postCellGid,postCellTags in postCellsTags.items() # for each postsyn cell
                                                for preCellGid, preCellTags in preCellsTags.items()  # for each presyn cell
                                                if postCellGid in self.gid2lid}  # check if postsyn is in this node
            connGids = self._disynapticBiasProb2(probMatrix, allRands, connParam['disynapticBias'], prePreGids, postPreGids)
            for preCellGid, postCellGid in connGids:
                for paramStrFunc in paramsStrFunc: # call lambda functions to get weight func args
                    connParam[paramStrFunc+'Args'] = {k:v if isinstance(v, Number) else v(preCellsTags[preCellGid],postCellsTags[postCellGid]) for k,v in connParam[paramStrFunc+'Vars'].items()}
                self._addCellConn(connParam, preCellGid, postCellGid) # add connection
        # standard probabilistic conenctions
        else:
            # calculate the conn preGids of the each pre and post cell
            # for postCellGid,postCellTags in sorted(postCellsTags.items()):  # for each postsyn cell
            for postCellGid,postCellTags in postCellsTags.items():  # for each postsyn cell  # for each postsyn cell
                if postCellGid in self.gid2lid:  # check if postsyn is in this node
                    for preCellGid, preCellTags in preCellsTags.items(): # for each presyn cell
                        probability = connParam['probabilityFunc'][preCellGid,postCellGid] if 'probabilityFunc' in connParam else connParam['probability']
                        if probability >= allRands[preCellGid,postCellGid]:
                            for paramStrFunc in paramsStrFunc: # call lambda functions to get weight func args
                                # update the relevant FuncArgs dict where lambda functions are known to exist in the corresponding FuncVars dict
                                for funcKey in funcKeys[paramStrFunc]:
                                    connParam[paramStrFunc + 'Args'][funcKey] = connParam[paramStrFunc + 'Vars'][funcKey](preCellTags, postCellTags)
                                # connParam[paramStrFunc+'Args'] = {k:v if isinstance(v, Number) else v(preCellTags,postCellTags) for k,v in connParam[paramStrFunc+'Vars'].items()}
                            if connParamLabel > 0 : input("about to add cell conn through _addCellConn")
                            #self._addCellConn(connParam, preCellGid, postCellGid) # add connection
                            ####################
                            # set final param values
                            paramStrFunc = self.connStringFuncParams
                            finalParam = {}
                            # Set final parameter values; initialize randomizer for string-based funcs that use rand to ensue replicability
                            # Note: could potentially speed up by generating list of values for all rand funcs used (e.g. rand.uniform())
                            # and then selecting a value from list based of pre- and post- gid -- that way only seed once at beginning in connectCells()
                            # Howeve, not clear if faster in all cases since need to generate values for len(pre)*len(post), whereas here only a subset
                            randSeeded = False
                            for param in paramStrFunc:
                                if param+'List' in connParam:
                                    finalParam[param] = connParam[param+'List'][preCellGid,postCellGid]
                                elif param+'Func' in connParam:
                                    if not randSeeded and 'rand' in connParam[param+'FuncArgs']:
                                        self.rand.Random123(preCellGid, postCellGid, sim.cfg.seeds['conn'])
                                        randSeeded = True
                                    finalParam[param] = connParam[param+'Func'](**connParam[param+'FuncArgs'])
                                else:
                                    finalParam[param] = connParam.get(param)
                            # get Cell object
                            postCell = self.cells[self.gid2lid[postCellGid]]
                            # convert synMech param to list (if not already)
                            if not isinstance(connParam.get('synMech'), list):
                                connParam['synMech'] = [connParam.get('synMech')]
                            # generate dict with final params for each synMech
                            paramPerSynMech = ['weight', 'delay', 'loc']
                            for i, synMech in enumerate(connParam.get('synMech')):
                                for param in paramPerSynMech:
                                    finalParam[param+'SynMech'] = finalParam.get(param)
                                    if len(connParam['synMech']) > 1:
                                        if isinstance (finalParam.get(param), list):  # get weight from list for each synMech
                                            finalParam[param+'SynMech'] = finalParam[param][i]
                                        elif 'synMech'+param.title()+'Factor' in connParam: # adapt weight for each synMech
                                            finalParam[param+'SynMech'] = finalParam[param] * connParam['synMech'+param.title()+'Factor'][i]
                                params = {'preGid': preCellGid,
                                'sec': connParam.get('sec'),
                                'loc': finalParam['locSynMech'],
                                'synMech': synMech,
                                'weight': finalParam['weightSynMech'],
                                'delay': finalParam['delaySynMech'],
                                'synsPerConn': finalParam['synsPerConn']}
                                # if 'threshold' in connParam: params['threshold'] = connParam.get('threshold')  # deprecated, use threshold in preSyn cell sec
                                if 'shape' in connParam: params['shape'] = connParam.get('shape')
                                if 'plast' in connParam: params['plast'] = connParam.get('plast')
                                if 'gapJunction' in connParam: params['gapJunction'] = connParam.get('gapJunction')
                                if sim.cfg.includeParamsLabel: params['label'] = connParam.get('label')
                                if connParamLabel > 0 :
                                    print("params:")
                                    print(params)
                                    #print(params.keys())
                                    #print(params.values())
                                    input("about to addConn with above params")
                                #postCell.addConn(params=params)
                                addConn_mod(cell=postCell, sim=sim, params=params)
        #############
        ##############
        #connFunc(preCellsTags, postCellsTags, connParam)  # call specific conn function
        print("connFunc takes:")
        print("\tpreCellsTags:")
        print(preCellsTags.keys())
        print("\tpreCellsTags:")
        print(postCellsTags.keys())
        print("\tconnParam:")
        print(connParam.keys())
        input("ran connFunc")
    # check if gap junctions in any of the conn rules
    if not gapJunctions and 'gapJunction' in connParam: gapJunctions = True
    if sim.cfg.printSynsAfterRule:
        nodeSynapses = sum([len(cell.conns) for cell in sim.net.cells])
        print(('  Number of synaptic contacts on node %i after conn rule %s: %i ' % (sim.rank, connParamLabel, nodeSynapses)))
    input()

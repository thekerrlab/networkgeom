from netpyne import specs
from netpyne.batch import Batch

def batchTauWeight():
	# Create variable of type ordered dictionary (NetPyNE's customized version)
	params = specs.ODict()

	# fill in with parameters to explore and range of values (key has to coincide with a variable in simConfig)
	params['weight_dist_factor'] = [0.5, 1, 5, 10]

	# create Batch object with paramaters to modify, and specifying files to use
	b = Batch(params=params, cfgFile='config.py', netParamsFile='network.py')

	# Set output folder, grid method (all param combinations), and run configuration
	b.batchLabel = 'connection_weight'
	b.saveFolder = 'network_data'
	b.method = 'grid'
	b.runCfg = {'type': 'mpi_bulletin',
				'script': 'run.py',
				'skip': True}

	# Run batch simulations
	b.run()

# Main code
if __name__ == '__main__':
	batchTauWeight()

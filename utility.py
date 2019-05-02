import statistics
import csv

# Find list of modes (most common elements) in list
# Time Complexity: O(n) amortized time
def modesFromList(list):
    # Initialisation, create dictionary with count
    dict = {}
    max = 0
    for element in list:
        if dict.get(element) == None:
            dict[element] = 0
        else:
            dict[element] += 1
            if dict[element] > max:
                max = dict[element]
    # Create list of modes
    modes = []
    for key, value in dict.items():
        if value == max:
            modes.append(key)
    return modes

# Prints a progress bar and percentage, progress between 0 and 1
def printProgress(progress):
    print("\t|", end="")
    progress *= 100
    increment = 5
    for i in range(1,round(100/increment) + 1):
        if round(progress,1) - increment*i >= 0:
            print("#", end="")
        else:
            print(" ", end="")
    print("| " + str(round(progress,1)) + "%")

# Returns dictionary of stats:
# {'sum': X, 'mean': Y, 'var': Z}
def getStats(list):
    stats = {}
    stats['sum'] = sum(list)
    stats['mean'] = statistics.mean(list)
    stats['var'] = statistics.variance(list)
    return stats

# Print spike weight statistics
def printStats(list):
    stats = getStats(list)
    print("\tSum: " + str(stats['sum']))
    print("\tMean: " + str(stats['mean']))
    print("\tVar: " + str(stats['var']))

# Save files
def saveMatrixInFile(list, filename):
    try:
        with open(filename, 'w') as file:
            writer = csv.writer(file)
            writer.writerow(list)
        print("Saved data to file " + filename)
    except:
        print("Failed to open or write to file")

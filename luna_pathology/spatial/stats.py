from scipy.spatial.distance import cdist
import numpy as np

# Helper function
def ret(count, ls):
	if ls:
		return count[0] if len(count) == 1 else count
	else:
		m = np.mean(count, axis=1)
		return m[0] if len(m) == 1 else m


# Counting K-function:
def CKfunction(p1XY, p2XY, R, ls = False):
	'''Measures the number of cells with phenotype 2 that are within
	   R units of phenotype 1 cells
	   p1XY: An Nx2 array representing the (X, Y) coordinates of cells with phenotype 1
	   p2XY: Same as p1XY but for cells with phenotype 2
	   R: The radius (or list of radii) to consider
	   ls: If True, returns an |R|x|p1XY| 2D array representing the number
	   of phenotype 2 cells within R units of each p1 cell for each R. If
	   false, returns the mean cell count for each R'''
	dists = cdist(p1XY,p2XY)
	counter = lambda r: np.sum((dists <= r), axis=1)
	try:
		count = [counter(r) for r in R]
	except TypeError:
		count = [counter(R)]
	return ret(np.array(count),ls)


# Intensity K-function:
def IKfunction(p1XY, p2XY, R, I, ls = False):
	'''Measure the total intensity of phenotype 2 cells
	within radius R of phenotype 1 cells
	I: An array of length |p2XY| representing the intensity of each '''
	dists = cdist(p1XY,p2XY)
	counter = lambda r: np.sum((dists <= r)*I, axis=1)
	try:
		count = [counter(r) for r in R]
	except TypeError:
		count = [counter(R)]
	return ret(np.array(count),ls)


# Intensity-Distance K-function:
def IDKfunction(p1XY, p2XY, R, I, ls = False):
	'''Measure the total intensity of phenotype 2 cells
	within radius R of phenotype 1 cells weighted for distance
	I: An array of length |p2XY| representing the intensity of each '''
	dists = cdist(p1XY,p2XY)
	counter = lambda r: np.sum((dists <= r)*I*(1/dists**3), axis=1)
	try:
		count = [counter(r) for r in R]
	except TypeError:
		count = [counter(R)]
	return ret(np.array(count),ls)

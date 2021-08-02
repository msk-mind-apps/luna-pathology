from scipy.spatial.distance import cdist
import numpy as np

# Helper function
def ret(count, ls):
	if ls:
		return count[0] if len(count) == 1 else count
	else:
		m = np.mean(count, axis=1)
		return m[0] if len(m) == 1 else m

def edge_correct(p1XY):
	xbound = [np.min(p1XY.T[0]),np.max(p1XY.T[0])]
	ybound = [np.min(p1XY.T[1]),np.max(p1XY.T[1])]
	weights = []
	for cell in p1XY:
		areas = np.zeros(2)
		# Check the X and Y edges
		for i in range(2):
			OP = np.min(np.abs(xbound-cell[i]))
			if OP < R:
				theta = 2 * np.arccos(OP/R)
				sector = R**2 * theta / 2
				triangle = 1/2 * R**2 * np.sin(theta)
				areas[i] = sector - triangle
		totarea = np.pi * R**2
		prop = (totarea - areas)/totarea
		weights.append(np.max(1/prop))
	return weights


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
	W = edge_correct(p1XY)
	counter = lambda r: np.sum((dists <= r), axis=1)*W
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

import pandas as pd
import os
import scipy.stats
import numpy as np
# stats = __import__("luna-pathology.luna_pathology.spatial.stats", fromlist=[None])
from stats import *

def runKfunction(detection_path,phenotype_path,method_data):

	dfiles = os.listdir(detection_path)
	pfiles = os.listdir(phenotype_path)

	# Perform some quick checks
	assert(len(dfiles) == len(pfiles))
	for i in range(len(dfiles)):
		assert(dfiles[i] == pfiles[i])

	print(f"Number of datapoints: {len(dfiles)}")

	# Create the data structure to store K function results
	data = {}
	for i in range(len(dfiles)):
		patient = dfiles[i].split("_")[0]
		data[patient] = {}
	for i in range(len(dfiles)):
		labels = dfiles[i].split("_")
		patient = labels[0]
		region = labels[1]
		data[patient][region] = []

	print(f"Number of patients: {len(data)}")

	# Loop through each file and fill out the data structure
	print("Computing the K function...")
	for i in range(len(dfiles)):
		print(i)
		dpath = detection_path + "/" + dfiles[i] + "/object_detection_results.tsv"
		ppath = phenotype_path + "/" + pfiles[i] + "/phenotypes.tsv"

		# Create the data frame
		df = pd.read_csv(dpath, sep='\t')
		df = df.drop(columns=["Class"])
		p = pd.read_csv(ppath, sep='\t')
		p = p.drop(columns=["Image", "Name", "Class", "Parent", "ROI"])
		df = pd.merge(df, p, on='cell_id',  how='left')

		# Unpack the method_data dictionary
		col1 = method_data["phenotype1"]["name"]
		val1 = method_data["phenotype1"]["value"]
		col2 = method_data["phenotype2"]["name"]
		val2 = method_data["phenotype2"]["value"]

		# Create the data arrays
		pheno1 = df[df[col1] == val1]
		pheno2 = df[df[col2] == val2]
		p1XY = np.array(pheno1[["Centroid X µm","Centroid Y µm"]])
		p2XY = np.array(pheno2[["Centroid X µm","Centroid Y µm"]])
		I = np.array(pheno2[method_data["intensity"]])
		assert (p1XY.size != 0), f"List of phenotype 1 cells ({val1}) is empty"
		assert (p2XY.size != 0), f"List of phenotype 2 cells ({val2}) is empty"

		# Identify the datapoint
		labels = dfiles[i].split("_")
		patient = labels[0]
		region = labels[1]
		fov = labels[4]

		# Compute the K function
		k = Kfunction(p1XY,p2XY,60,ls=True,intensity=I)

		assert(0==5)

		d = {
			"Moment":np.array([np.mean(k),np.var(k),scipy.stats.skew(k),scipy.stats.kurtosis(k)]),
			"N":len(p1XY)
		}
		data[patient][region].append(d)

	# Perform the aggregation across replicates in a region weighting by |p1XY|
	print("Performing aggregation")
	for i in data:
		for j in data[i]:
			weight = 0
			moments = np.array([0.0,0.0,0.0,0.0])
			for k in data[i][j]:
				weight += k["N"]
				moments += k["Moment"] * k["N"]
			moments /= weight
			data[i][j] = moments

	for i in data:
		print(i)
		for j in data[i]:
			print(f"  {j}: {data[i][j]}")













dr = "/gpfs/mskmind_ess/vazquezi/data/transfers/spectrum/results/mpif/v11"
d_path = dr + "/qupath/outputs/format_detection/fov"
p_path = dr + "/cell-type/outputs/apply_thresholds/fov"
p1 = {
	"name" : "cell_type",
	'value' : 'panCK+'
}
p2 = {
	"name" : "CD68_state",
	'value' : 'CD68+'
}
method_data = {
	"phenotype1" : p1,
	"phenotype2" : p2,
	"intensity" : 'Cell: PDL1 mean'

}
runKfunction(d_path, p_path, method_data)














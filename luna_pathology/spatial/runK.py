import pandas as pd
import os
import scipy.stats
import numpy as np
from copy import deepcopy
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

	# Load the metadata and set up the data structure
	data = {}
	metadata = {}
	fovmeta = pd.read_csv("fov_metadata.tsv", sep='\t')
	patient_id = fovmeta["patient_id"]
	tumor_site_short = fovmeta["tumor_site_short"]
	isabl_id = fovmeta["isabl_id"]
	for patient in patient_id:
		data[patient] = {}
	for i in range(len(patient_id)):
		data[patient_id[i]][tumor_site_short[i]] = []
		metadata[isabl_id[i]] = {"patient":patient_id[i],"site":tumor_site_short[i]}
	data = {"count":deepcopy(data),"intensity":deepcopy(data),"distance":deepcopy(data)}

	# Loop through each file and compute the K function
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
		R = method_data["R"]
		count = method_data["count"]
		distance = method_data["distance"]

		# Create the data arrays
		pheno1 = df[df[col1] == val1]
		pheno2 = df[df[col2] == val2]
		p1XY = np.array(pheno1[["Centroid X µm","Centroid Y µm"]])
		p2XY = np.array(pheno2[["Centroid X µm","Centroid Y µm"]])
		I = np.array(pheno2[method_data["intensity"]])
		assert (p1XY.size != 0), f"List of phenotype 1 cells ({val1}) is empty"
		assert (p2XY.size != 0), f"List of phenotype 2 cells ({val2}) is empty"

		patient_metadata = metadata[df["Image"][0]]

		# Compute the K function
		K = Kfunction(p1XY,p2XY,R,ls=True,count=count,intensity=I,distance=distance)
		
		# Unpack and fill out the aggregation data structure
		keys = K.keys()
		for key in keys:
			data[key][patient_metadata["patient"]][patient_metadata["site"]].extend(K[key])

	# Perform the aggregation across replicates in a region
	print("Performing aggregation")
	for key in keys:
		for patient in data[key]:
			for region in data[key][patient]:
				arr = data[key][patient][region]
				moments = np.array([np.mean(arr),np.var(arr),scipy.stats.skew(arr),scipy.stats.kurtosis(arr)])
				data[key][patient][region] = moments

	# Save the output
	title = f"p1={val1},p2={val2},I={method_data['intensity']},R={R}.npy"
	np.save(title,  data) 


if __name__ == "__main__":
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
		"R" : 60,
		"count" : True,
		"intensity" : 'Cell: PDL1 mean',
		"distance" : False
	}

	runKfunction(d_path, p_path, method_data)





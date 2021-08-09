import pandas as pd
import os
import scipy.stats
import numpy as np
import csv
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

	# Load the metadata files
	fovmeta = pd.read_csv("fov_metadata.tsv", sep='\t')
	samplemeta = pd.read_csv("sample_metadata.tsv", sep='\t')
	
	# Turn the metadata files into dictionaries so we can look up information later
	fovmetadata = dict(zip(fovmeta["isabl_id"],fovmeta.to_dict('records')))
	samplemetadata = dict(zip(samplemeta["pici_id"], samplemeta.to_dict('records')))

	# Unpack the method_data dictionary
	col1 = method_data["phenotype1"]["name"]
	val1 = method_data["phenotype1"]["value"]
	col2 = method_data["phenotype2"]["name"]
	val2 = method_data["phenotype2"]["value"]
	R = method_data["R"]
	count = method_data["count"]
	distance = method_data["distance"]

	# Check if the computation has been run with this R before
	filename = f"p1={val1},p2={val2},I={method_data['intensity']}.tsv"
	if os.path.exists(filename):
		file_df = pd.read_csv(filename, sep='\t')
		Rs = set(file_df["radius"])
		if R in Rs:
			msg = f"This computation has already been run for R = {R}"
			assert 0, msg

	# Loop through each file and compute the K function
	print("Computing the K function...")
	data = {"count":{},"intensity":{},"distance":{}}
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

		# Look up the metadata
		isabl_id = df["Image"][0]
		fovmeta = fovmetadata[isabl_id]
		pici_id = fovmeta["pici_id"]
		samplemeta = samplemetadata[pici_id]

		# Filter for qc_status == 'Pass' in sample_metadata and
		# fov_status == 'Pass' in fov_metadata
		if (fovmeta["fov_status"] != "Pass") or (samplemeta["qc_status"] != "Pass"):
			continue

		# Create the data arrays
		pheno1 = df[df[col1] == val1]
		pheno2 = df[df[col2] == val2]
		p1XY = np.array(pheno1[["Centroid X µm","Centroid Y µm"]])
		p2XY = np.array(pheno2[["Centroid X µm","Centroid Y µm"]])
		I = np.array(pheno2[method_data["intensity"]])
		if p1XY.size == 0:
			print(f"WARNING: List of phenotype 1 cells ({val1}) is empty for {isabl_id}")
		if p2XY.size == 0:
			print(f"WARNING: List of phenotype 2 cells ({val2}) is empty for {isabl_id}")

		# Compute the K function
		K = Kfunction(p1XY,p2XY,R,ls=True,count=count,intensity=I,distance=distance)

		# Unpack and fill out the aggregation data structure
		for key in K:
			if pici_id in data[key]:
				np.append(data[key][pici_id],K[key])
			else:
				data[key][pici_id] = K[key]

	# Save the output
	dataframe = []
	for key in data:
		for pici_id in data[key]:
			arr = data[key][pici_id]
			dataframe.append({
				"pici_id":pici_id,
				"radius":R,
				"function":key,
				"mean":np.mean(arr),
				"variance":np.var(arr),
				"skew":scipy.stats.skew(arr),
				"kurtosis":scipy.stats.kurtosis(arr)
			})

	# Store the moments in a new/existing .tsv
	output_file = open(filename, 'a+')
	dict_writer = csv.DictWriter(output_file, dataframe[0].keys(), delimiter='\t')
	if os.stat(filename).st_size == 0:
		dict_writer.writeheader()	
	dict_writer.writerows(dataframe)
	output_file.close()


# Driver function to produce the .tsv output
if __name__ == "__main__":
	dr = "/gpfs/mskmind_ess/vazquezi/data/transfers/spectrum/results/mpif/v11"
	d_path = dr + "/qupath/outputs/format_detection/fov"
	p_path = dr + "/cell-type/outputs/apply_thresholds/fov"
	p1 = {
		"name" : "cell_type",
		'value' : 'panCK+'
	}
	p2 = {
		"name" : "cell_type",
		'value' : 'CD8+'
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





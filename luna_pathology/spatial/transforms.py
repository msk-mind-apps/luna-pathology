""" Higher-level transformation functions """

import pandas as pd
import scipy.stats
import numpy as np
from stats import *
import pyarrow
pyarrow.set_cpu_count(1)

import glob

def runKfunction(cell_paths, method_data):
	pyarrow.set_cpu_count(1)

	cell_paths = np.squeeze(list(cell_paths)).tolist()

	agg_k_data = {}

	for cell_path in cell_paths:

		df = pd.read_parquet( cell_path ) 

		pheno1_col    = method_data["phenotype1"]["name"]
		pheno1_val    = method_data["phenotype1"]["value"]
		pheno2_col    = method_data["phenotype2"]["name"]
		pheno2_val    = method_data["phenotype2"]["value"]
		R             = method_data["R"]
		count         = method_data["count"]
		distance      = method_data["distance"]
		intensity_col = method_data["intensity"]
			
		# Look up the index for this slice
		index = df[method_data['index']].iloc[0]

		# Create the data arrays
		pheno1 = df[df[pheno1_col] == pheno1_val]
		pheno2 = df[df[pheno2_col] == pheno2_val]
		p1XY = np.array(pheno1[["Centroid X µm","Centroid Y µm"]])
		p2XY = np.array(pheno2[["Centroid X µm","Centroid Y µm"]])
		I    = np.array(pheno2[intensity_col])

		if p1XY.size == 0:
			print(f"WARNING: List of phenotype 1 cells ({pheno1_val}) is empty for {index}")
		if p2XY.size == 0:
			print(f"WARNING: List of phenotype 2 cells ({pheno2_val}) is empty for {index}")

		# Compute the K function
		print (f"Running... {cell_path}")

		fov_k_data = Kfunction(p1XY, p2XY, R, ls=True, count=count, intensity=I, distance=distance)

		for key in fov_k_data:
			if key in agg_k_data:
				np.append(agg_k_data[key],fov_k_data[key])
			else:
				agg_k_data[key] = fov_k_data[key]

	data_out = {}

	for kfunct in agg_k_data.keys():
		arr = agg_k_data[kfunct]
		if len(arr)==0: arr=[0]
		data_out.update( 
			{
				f"{pheno1_col}{pheno1_val}_{pheno2_col}{pheno2_val}_{R}_{kfunct}_{intensity_col}_mean": np.mean(arr),
				f"{pheno1_col}{pheno1_val}_{pheno2_col}{pheno2_val}_{R}_{kfunct}_{intensity_col}_variance": np.var(arr),
				f"{pheno1_col}{pheno1_val}_{pheno2_col}{pheno2_val}_{R}_{kfunct}_{intensity_col}_skew": scipy.stats.skew(arr),
				f"{pheno1_col}{pheno1_val}_{pheno2_col}{pheno2_val}_{R}_{kfunct}_{intensity_col}_kurtosis": scipy.stats.kurtosis(arr)
			}
		)

	df_slice_out = pd.DataFrame(data_out, index=[0]).astype(np.float64)
	df_slice_out['main_index'] = index
	df_slice_out = df_slice_out.set_index('main_index')

	print (df_slice_out)

	return df_slice_out

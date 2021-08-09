import numpy as np
import pandas as pd
import scipy.stats

fovmeta = pd.read_csv("fov_metadata.tsv", sep='\t')
samplemeta = pd.read_csv("sample_metadata.tsv", sep='\t')
samplemetadata = dict(zip(samplemeta["pici_id"], samplemeta.to_dict('records')))

val1 = "panCK+"
val2 = "CD8+"
I = "Cell: PDL1 mean"
filename = f"p1={val1},p2={val2},I={I}.tsv"
R = "60"
moments = ["mean","variance","skew","kurtosis"]

data = pd.read_csv(filename, sep='\t')
data = data[data.radius == 60]
countdata = data[data.function == "count"]
intensitydata = data[data.function == "intensity"]

# 1. The effect of site specificity on cell-cell interactions
# This you can study by joining the tumor_supersite column in
# sample_metadata, and aggregating K-statistics across FOVs based
# on that variable


sitelist = ["Adnexa", "Omentum", "Upper Quadrant", "Peritoneum", "Bowel", "Other"]
sites = [samplemetadata[i]["tumor_supersite"] for i in countdata.pici_id]

arr = intensitydata

for i in range(5):
	for j in range(5-i):
		s1 = sitelist[i]
		s2 = sitelist[i+j+1]

		type1 = arr[[s == s1 for s in sites]]
		type2 = arr[[s == s2 for s in sites]]

		for k in range(4):
			a = type1[moments[k]]
			b = type2[moments[k]]
			p = scipy.stats.ttest_ind(a,b).pvalue
			print(f"{p}: {s1} {s2} {moments[k]}")


# 2. The effect of DNA repair deficiency in tumour cells of a
# subset of these patients. These are best identified either
# based on BRCA1/2 mutations (e.g. from IMPACT) or using
# whole-genome sequencing to infer signatures of DNA repair
# deficiency. You should be able to join the table in this git
# repo by patient_id, and then use the consensus_signature and
# consensus_signature_short columns to try and look for
# associations based on the K-statistic
# (https://github.com/shahcompbio/spectrum-tme/blob/master/tables/mutational_signatures.xlsx).







# Metastatic vs Primary

arr = intensitydata
m = [samplemetadata[i]["tumor_type"]=="Metastasis" for i in countdata.pici_id]
p = [samplemetadata[i]["tumor_type"]=="Primary" for i in countdata.pici_id]

m = arr[m]
p = arr[p]

for k in range(4):
	a = m[moments[k]]
	b = p[moments[k]]
	pval = scipy.stats.ttest_ind(a,b).pvalue
	print(f"{pval}: {moments[k]}")


















import pandas as pd
import scipy.stats
import numpy as np
from transforms import runKfunction
import pyarrow
pyarrow.set_cpu_count(1)

import glob
import dask
import dask.dataframe as dd
from dask.distributed import Client


# Driver function to produce the .tsv output
if __name__ == "__main__":
	client = Client(threads_per_worker=1, n_workers=4)

	p1 = {
		"name" : "phenotype_short",
		'value' : 'CD8+'
	}
	p2 = {
		"name" : "phenotype_short",
		'value' : 'CD8+'
	}
	method_data = {
		"index": "pici_id",
		"phenotype1" : p1,
		"phenotype2" : p2,
		"R" : 60,
		"count" : True,
		"intensity" : 'Cell: PDL1 sum',
		"distance" : True
	}

	d_runKfunction =  dask.delayed(runKfunction)

	outputs = []
	ids = set()

	for file in glob.glob("/gpfs/mskmindhdp_emc/data_staging/OVARIAN_SPECTRUM/tables/MPIF_CELL_DATA_CD_PD_PANCK/*"):
		print (file)
		ids.add( str(file).split('/')[-1].split('.')[0].replace('_CD68', '') )

	for id in ids:
		cell_slices = [file for file in glob.glob(f"/gpfs/mskmindhdp_emc/data_staging/OVARIAN_SPECTRUM/tables/MPIF_CELL_DATA_CD_PD_PANCK/*{id}*")]
		delayed = d_runKfunction(cell_slices, method_data)
		outputs.append(delayed)

	dd.from_delayed(outputs).repartition(npartitions=5).to_parquet("/gpfs/mskmindhdp_emc/data_staging/OVARIAN_SPECTRUM/tables/BY_SITE_KFUNC_CD8_NEAR_CD8/")





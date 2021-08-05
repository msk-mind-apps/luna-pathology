import numpy as np

val1 = "panCK+"
val2 = "CD68+"
I = "Cell: PDL1 mean"
R = "60"

title = f"p1={val1},p2={val2},I={I},R={R}.npy"
data = np.load(title, allow_pickle=True).item()

for key in data:
	print(key)
	for patient in data[key]:
		print(f"  {patient}")
		for site in data[key][patient]:
			print(f"    {site}: {data[key][patient][site]}")


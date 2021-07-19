from luna_pathology.spatial.stats import *
import numpy as np

def test():
	r = 50
	R = np.linspace(1,100,10)
	p1 = np.random.rand(41,2)
	p2 = np.random.rand(17,2)
	I = np.random.rand(17)
	funcs = [CKfunction, IKfunction, IDKfunction]
	for func in funcs:
	    if func.__name__ == "CKfunction":
	        F00 = func(p1,p2,r,ls=True)
	        F01 = func(p1,p2,r,ls=False)
	        F10 = func(p1,p2,R,ls=True)
	        F11 = func(p1,p2,R,ls=False)
	    else:
	        F00 = func(p1,p2,r,I,ls=True)
	        F01 = func(p1,p2,r,I,ls=False)
	        F10 = func(p1,p2,R,I,ls=True)
	        F11 = func(p1,p2,R,I,ls=False)
	        
	    assert(F00.shape == (len(p1),))
	    assert(F01.shape == ())
	    assert(F10.shape == (len(R),len(p1)))
	    assert(F11.shape == (len(R),))
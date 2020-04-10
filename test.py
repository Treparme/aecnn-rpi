import numpy as np
from anc import ANC

class IN():
    def get(self):
        return np.zeros(blocksize)

class OUT():
    def put(self, output):
        print("output")

qout = OUT()
qout1 = OUT()
qin = IN()
qin1 = IN()
delay = 100
blocksize = 500

anc = ANC(qout, qout1, qin, qin1, delay, blocksize)
anc.start()
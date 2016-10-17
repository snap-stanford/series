import cPickle as pickle
import os
import sys
from datetime import datetime
from datetime import timedelta
import pandas as pd
import numpy as np

if len(sys.argv) < 2:
    print "Usage: <script> <driver>"
    exit(0)

driver = sys.argv[1].strip()

blinker_sensor = 's_gateway_72_bh_blinker_li'
blinker_idx = 1
sensors = {}
bool_indices = []
with open('../../signals_with_dtype') as fp:
    index = 2
    for line in fp:
        line = line.strip().split()
        if line[1] != 'bool':
            index += 1
            continue
        else:
            sensors[index] = line[0]
            bool_indices.append(index)
            if line[0] == blinker_sensor:
                blinker_idx = index
        index += 1
i = 0
for sensor in sensors:
    if sensor == blinker_sensor:
        blinker_idx = 2 + i
        break
    i = i + 1
#blinker_idx = 1802
print blinker_idx
#bcc37725-fb79-4e4d-af83-69246a065228'
files = os.listdir('/lfs/local/0/abhisg/vw/driver_date/')
raw_data_X = []
raw_data_Y = []
counter = 0
pos_idx = []
neg_idx = []
idx = 0
for file in files:
    #if counter == 2:
    #    break
    if driver in file:
        data = pd.read_csv('/lfs/local/0/abhisg/vw/driver_date/'+file,sep='\t',header=None,low_memory=False)
        data = data[bool_indices]
        #print data.columns.values
        data = data.fillna(method='ffill')
        xcols = [col for col in data.columns if col != blinker_idx]
        data_X = data[xcols].values
        data_Y = data[blinker_idx].values
        for i in xrange(1,len(data_X)):
            if data_Y[i] == 't' and data_Y[i-1] != 't':
                raw_data_Y.append([0,1])
                pos_idx.append(idx)
            else:
                raw_data_Y.append([1,0])
                neg_idx.append(idx)
            raw_data_X.append(map(lambda x:1 if x == 't' else 0,data_X[i-1,:]))
            idx += 1
        #print '/lfs/local/0/abhisg/vw/driver_date/'+file, len([v for v in raw_data_Y if v == 1])
        counter = counter + 1
raw_data_X = np.array(raw_data_X)
raw_data_Y = np.array(raw_data_Y)
#print raw_data_X, raw_data_Y
pos_idx = np.array(pos_idx)
neg_idx = np.array(neg_idx)
np.random.shuffle(neg_idx)
neg_idx = neg_idx[:pos_idx.shape[0]]
print pos_idx.shape,neg_idx.shape
idx = np.concatenate((pos_idx,neg_idx))
np.random.shuffle(idx)
print idx.shape
train_idx = int(0.9*idx.shape[0])
np.save('/lfs/local/0/abhisg/vw/driver_data/single_driver_data_X_train_'+driver,raw_data_X[idx[:train_idx],:])
np.save('/lfs/local/0/abhisg/vw/driver_data/single_driver_data_Y_train_'+driver,raw_data_Y[idx[:train_idx],:])
np.save('/lfs/local/0/abhisg/vw/driver_data/single_driver_data_X_test_'+driver,raw_data_X[idx[train_idx:],:])
np.save('/lfs/local/0/abhisg/vw/driver_data/single_driver_data_Y_test_'+driver,raw_data_Y[idx[train_idx:],:])

    

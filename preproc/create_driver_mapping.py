import os
from datetime import datetime
from datetime import timedelta
import cPickle as pickle

driver_carid = {}
with open('../sessions.tsv') as fp:
    for line in fp:
        line = line.strip().split('\t')
        start_time = datetime.strptime(line[1],"%Y-%m-%d %H:%M:%S.%f")
        start_time = start_time.replace(minute=0,second=0,microsecond=0)
        #start_time = datetime.strptime(line[1],"%Y-%m-%d %H")
        end_time = datetime.strptime(line[2],"%Y-%m-%d %H:%M:%S.%f")
        if line[4] not in driver_carid:
            driver_carid[line[4]] = {}
        while start_time < end_time:
            time = datetime.strftime(start_time,"%Y%m%d_%H")
            driver_carid[line[4]][time] = line[0]
            start_time += timedelta(hours=1)
for driver in driver_carid:
    print driver,driver_carid[driver]
pickle.dump(driver_carid,open('driver_mapping.pkl','w+'))





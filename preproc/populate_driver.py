import cPickle as pickle
import os
import sys
from datetime import datetime
from datetime import timedelta

if len(sys.argv) < 3:
    print "Usage: <script> <date_hour> <driver>"
    exit(0)

time = sys.argv[1].strip()
driver = sys.argv[2].strip()

driver_mapping = pickle.load(open('driver_mapping.pkl'))
if time not in driver_mapping[driver]:
    print "not relevant"
    exit(0)
car = driver_mapping[driver][time]

sensors = {}
sensor_pointer = {}
location = '/lfs/local/0/abhisg/vw/hour_data_2/'+time
filenames = os.listdir(location)
#filenames = ['s_gateway_72_bh_blinker_li.tsv']
starttime = datetime.strptime(time,"%Y%m%d_%H")
endtime = starttime + timedelta(hours=1)
sensorlist = []
with open('../../signals_only') as fp:
    for line in fp:
        line = line.strip()
        sensorlist.append(line)
        sensors[line] = []
        sensor_pointer[line] = 0
        if line+'.tsv' in filenames:
            sensors[line] = []
            with open(location+'/'+line+'.tsv') as fl:
                for line2 in fl:
                    line2 = line2.strip().split('\t')
                    line2[1] = datetime.strptime(line2[1],"%Y-%m-%d %H:%M:%S.%f")
                    if line2[0] != car:
                        continue
                    else:
                        sensors[line].append(line2[1:])
        print line,len(sensors[line])

filepointer = open('/lfs/local/0/abhisg/vw/driver_date/'+time+'_'+driver+'.tsv','w+')
while starttime < endtime:
    thisline = datetime.strftime(starttime,"%Y-%m-%d %H:%M:%S.%f")+'\t'+driver+'\t'
    for i in xrange(len(sensorlist)):
        sensor = sensorlist[i]
        value = ''
        counter = sensor_pointer[sensor]
        length = len(sensors[sensor])
        cache = sensors[sensor]
        while counter < length and starttime > cache[counter][0]:
            counter += 1
        if counter < length and cache[counter][0] - starttime < timedelta(microseconds=100000):
            value = cache[counter][1]
            sensor_pointer[sensor] = counter + 1
        elif counter == length:
            sensor_pointer[sensor] = counter
        thisline += value+'\t'
    starttime = starttime + timedelta(microseconds=100000)
    thisline = thisline[:-1]
    filepointer.write(thisline+'\n')
filepointer.close()

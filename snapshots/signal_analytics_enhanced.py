from datetime import datetime
from datetime import timedelta
import sys
from collections import Counter

cars = {}
delta = timedelta(0)
with open('/dfs/scratch0/dataset/vw/tsv_sorted/sessions.tsv') as fp:
    for line in fp:
        line = line.strip().split('\t')
        if line[0] not in cars:
            cars[line[0]] = []
        cars[line[0]].append((datetime.strptime(line[1],"%Y-%m-%d %H:%M:%S.%f"),datetime.strptime(line[2],"%Y-%m-%d %H:%M:%S.%f"),line[4]))
        delta += cars[line[0]][-1][1] - cars[line[0]][-1][0] 
#print delta.total_seconds()
if len(sys.argv) < 2:
    print "Usage : <script> <filename>"
    exit(0)

drivers = {}
for car in cars:
    for v in cars[car]:
        if v[2] not in drivers:
            drivers[v[2]] = [0,0]

fname = sys.argv[1]
with open('/dfs/scratch0/dataset/vw/tsv_sorted/'+fname) as fp:
    current_car = ""
    idx = 0
    #current_true = 0
    #current_false = 0
    current_val = ''
    timediff = timedelta(0)
    #truetime = timedelta(0)
    #falsetime = timedelta(0)
    times = Counter()
    counts = Counter()
    last_time = None
    for line in fp:
        line = line.strip().split('\t')
        current_time = datetime.strptime(line[1],"%Y-%m-%d %H:%M:%S.%f")
        if current_car == "":
            current_car = line[0]
            if current_car not in cars:
                continue
            last_time = cars[current_car][idx][0]
            current_val = not line[2]
            #print "set time 1"
            #if line[2] == 't':
            #    current_true = 1
            #else:
            #    current_false = 1
        #try:
        print line[2],idx,len(cars[current_car]),line[0],current_time, last_time, cars[current_car][idx][0], cars[current_car][idx][1]
        #except:
        #    print "overflown"
        if line[0] == current_car and line[0] in cars:
            #if current_val == line[2]:
            #    continue
            if idx == len(cars[current_car]) or cars[current_car][idx][0] - current_time > timedelta(minutes=10):
                if idx < len(cars[current_car]):
                    last_time = cars[current_car][idx][0]
                continue
            elif cars[current_car][idx][0] - current_time <= timedelta(minutes=10) and current_time - cars[current_car][idx][1] <= timedelta(minutes=10):
                timediff += max(timedelta(0),current_time - last_time)
                if line[2] != current_val:
                    counts[line[2]] += 1
                if current_val != '':
                    times[current_val] += max(0,(current_time - last_time).total_seconds())
                current_val = line[2]
                last_time = current_time
            else:
                idx_copy = idx
                while idx < len(cars[current_car]) and current_time - cars[current_car][idx][1] > timedelta(minutes=10):
                    idx = idx + 1
                times[current_val] += max(0,(cars[current_car][idx_copy][1] - last_time).total_seconds())
                if timediff > timedelta(0):
                    counter = ""
                    timer = ""
                    for v in list(counts):
                        counter += str(counts[v]) + '\t'
                        timer += str(times[v]) + '\t'
                    print counter[:-1],timediff.total_seconds(),timer[:-1]
                    #print current_true,current_false,timediff.total_seconds(),truetime.total_seconds(),falsetime.total_seconds()
                    #drivers[cars[current_car][idx_copy][2]][0] += truetime.total_seconds()
                    #drivers[cars[current_car][idx_copy][2]][1] += falsetime.total_seconds()
                    timediff = timedelta(0)
                    times = Counter()
                    counts = Counter()
                    #truetime = timedelta(0)
                    #falsetime = timedelta(0)
                    #current_true = 0
                    #current_false = 0
                if idx < len(cars[current_car]):
                    if cars[current_car][idx][0] - current_time > timedelta(minutes=10):
                        last_time = cars[current_car][idx][0]
                        continue
                    else:
                        current_car = line[0]
                        current_val = line[2]
                        last_time = current_time
                        times = Counter()
                        counts = Counter()
                        timediff = timedelta(0)
                        counts[current_val] += 1
                        #print "set time 3"
                        #if current_val == 't':
                        #    current_true = 1
                        #    current_false = 0
                        #else:
                        #    current_false = 1
                        #    current_true = 0
        elif line[0] != current_car and line[0] in cars:
            #print "car changed"
            idx_copy = idx-1
            v1 = 0
            if cars[line[0]][v1][0] - current_time >= timedelta(minutes=10):
                #print current_time,cars[line[0]][v][0]
                continue
            else:
                #print "looping"
                while v1 < len(cars[line[0]]) and current_time - cars[line[0]][v1][1] > timedelta(minutes=10):
                    v1 = v1 + 1
                if v1 < len(cars[line[0]]):
                    if cars[line[0]][v1][0] - current_time >= timedelta(minutes=10):
                        continue
                    else:
                        times[current_val] += max(0, (cars[current_car][idx_copy][1] - last_time).total_seconds())
                        if timediff > timedelta(0):
                            counter = ""
                            timer = ""
                            for v in list(counts):
                                counter += str(counts[v]) + '\t'
                                timer += str(times[v]) + '\t'
                            print counter[:-1],timediff.total_seconds(),timer[:-1]
                            #print current_true,current_false,timediff.total_seconds(),truetime.total_seconds(),falsetime.total_seconds()
                            #drivers[cars[current_car][idx_copy][2]][0] += truetime.total_seconds()
                            #drivers[cars[current_car][idx_copy][2]][1] += falsetime.total_seconds()
                        current_car = line[0]
                        current_val = line[2]
                        last_time = current_time
                        timediff = timedelta(0)
                        #print "set time 3"
                        times = Counter()
                        counts = Counter()
                        counts[current_val] += 1
                        idx = v1
                else:
                    times[current_val] += max(0, (cars[current_car][idx_copy][1] - last_time).total_seconds())
                    #if current_val == 't':
                    #    truetime += max(timedelta(0), cars[current_car][idx_copy][1] - last_time)
                    #else:
                    #    falsetime += max(timedelta(0), cars[current_car][idx_copy][1] - last_time)
                    if timediff > timedelta(0):
                        counter = ""
                        timer = ""
                        for v in list(counts):
                            counter += str(counts[v]) + '\t'
                            timer += str(times[v]) + '\t'
                        print counter[:-1],timediff.total_seconds(),timer[:-1]
    
    if current_car in cars:
        times[current_val] += max(0, (cars[current_car][idx_copy][1] - last_time).total_seconds())
    counter = ""
    timer = ""
    for v in list(counts):
        counter += str(counts[v]) + '\t'
        timer += str(times[v]) + '\t'
    print counter[:-1],timediff.total_seconds(),timer[:-1]

#for driver in drivers:
#    print driver,drivers[driver][0]/(drivers[driver][0]+drivers[driver][1]),drivers[driver][1]/(drivers[driver][0]+drivers[driver][1])

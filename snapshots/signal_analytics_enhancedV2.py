from datetime import datetime
from datetime import timedelta
import sys
from collections import Counter

def getStats(collect,starttime,endtime):
    times = Counter()
    counts = Counter()
    prev_time = starttime
    for i in xrange(len(collect)-1):
        time[collect[i][0]] += max(0,(collect[i+1][1]-collect[i][1]).total_seconds())
        if collect[i][0] != collect[i+1][0]:
            counts[collect[i][0]] += 1
    time[collect[len(collect)-1][0]] += max(0,(endtime-collect[len(collect)-1][1]).total_seconds())
    counts[collect[len(collect)-1][0]] += 1
    return (times,counts)


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
    cache = []
    for line in fp:
        line = line.strip().split('\t')
        current_time = datetime.strptime(line[1],"%Y-%m-%d %H:%M:%S.%f")
        if current_car == "":
            current_car = line[0]
            if current_car not in cars:
                continue
        if line[0] == current_car and line[0] in cars:
            #if current_val == line[2]:
            #    continue
            if idx == len(cars[current_car]) or cars[current_car][idx][0] - current_time > timedelta(minutes=10):
                continue
            elif cars[current_car][idx][0] - current_time <= timedelta(minutes=10) and current_time - cars[current_car][idx][1] <= timedelta(minutes=10):
                cache.append((line[2],current_time))
            else:
                idx_copy = idx
                while idx < len(cars[current_car]) and current_time - cars[current_car][idx][1] > timedelta(minutes=10):
                    idx = idx + 1
                #times[current_val] += max(0,(cars[current_car][idx_copy][1] - last_time).total_seconds())
                if len(cache) > 0:
                    counts,times = getStats(cache,cars[current_car][idx_copy][0],cars[current_car][idx_copy][1])
                    counter = ""
                    timer = ""
                    for v in list(counts):
                        counter += str(counts[v]) + '\t'
                        timer += str(times[v]) + '\t'
                    print counter[:-1],timediff.total_seconds(),timer[:-1]
                    cache = []
                if idx < len(cars[current_car]):
                    if cars[current_car][idx][0] - current_time > timedelta(minutes=10):
                        continue
                    else:
                        cache.append((line[2],current_time))
        elif line[0] != current_car and line[0] in cars:
            #print "car changed"
            idx_copy = idx-1
            v1 = 0
            if cars[line[0]][v1][0] - current_time >= timedelta(minutes=10):
                continue
            else:
                #print "looping"
                while v1 < len(cars[line[0]]) and current_time - cars[line[0]][v1][1] > timedelta(minutes=10):
                    v1 = v1 + 1
                if v1 < len(cars[line[0]]):
                    if cars[line[0]][v1][0] - current_time >= timedelta(minutes=10):
                        continue
                    else:
                        if len(cache) > 0:
                            counts,times = getStats(cache,cars[current_car][idx_copy][0],cars[current_car][idx_copy][1])
                            counter = ""
                            timer = ""
                            for v in list(counts):
                                counter += str(counts[v]) + '\t'
                                timer += str(times[v]) + '\t'
                            print counter[:-1],timediff.total_seconds(),timer[:-1]
                            cache = []
                        idx = v1
                        current_car = line[0]
                        cache.append((line[2],current_time))
                else:
                    if len(cache) > 0:
                        counts,times = getStats(cache,cars[current_car][idx_copy][0],cars[current_car][idx_copy][1])
                        counter = ""
                        timer = ""
                        for v in list(counts):
                            counter += str(counts[v]) + '\t'
                            timer += str(times[v]) + '\t'
                        print counter[:-1],timediff.total_seconds(),timer[:-1]
                        cache = []
    counts,times = getStats(cache,cars[current_car][idx-1][0],cars[current_car][idx-1][1])    
    counter = ""
    timer = ""
    for v in list(counts):
        counter += str(counts[v]) + '\t'
        timer += str(times[v]) + '\t'
    print counter[:-1],timediff.total_seconds(),timer[:-1]

#for driver in drivers:
#    print driver,drivers[driver][0]/(drivers[driver][0]+drivers[driver][1]),drivers[driver][1]/(drivers[driver][0]+drivers[driver][1])

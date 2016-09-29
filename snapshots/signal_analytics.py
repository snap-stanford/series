from datetime import datetime
from datetime import timedelta
import sys

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
    current_true = 0
    current_false = 0
    current_val = 't'
    timediff = timedelta(0)
    truetime = timedelta(0)
    falsetime = timedelta(0)
    last_time = None
    for line in fp:
        line = line.strip().split('\t')
        current_time = datetime.strptime(line[1],"%Y-%m-%d %H:%M:%S.%f")
        if current_car == "":
            current_car = line[0]
            if current_car not in cars:
                continue
            current_val = not line[2]
            last_time = cars[current_car][idx][0]
            #print "set time 1"
            if line[2] == 't':
                current_true = 1
            else:
                current_false = 1
        #try:
        #    print line[2],idx,len(cars[current_car]),line[0],current_time, last_time, cars[current_car][idx][0], cars[current_car][idx][1],truetime.total_seconds(),falsetime.total_seconds()
        #except:
        #    print "overflown"
        if line[0] == current_car and line[0] in cars:
            #if current_val == line[2]:
            #    continue
            if idx == len(cars[current_car]) or cars[current_car][idx][0] - current_time > timedelta(minutes=5):
                try:
                    last_time = cars[current_car][idx][0]
                except:
                    ab = 10
                continue
            elif cars[current_car][idx][0] - current_time <= timedelta(minutes=5) and current_time - cars[current_car][idx][1] <= timedelta(minutes=5):
                timediff += max(timedelta(0),current_time - last_time)
                if line[2] == 't':
                    if current_val == 'f':
                        falsetime += max(timedelta(0),current_time - last_time)
                        current_true += 1
                    else:
                        truetime += max(timedelta(0),current_time - last_time)
                else:
                    if current_val == 't':
                        truetime += max(timedelta(0),current_time - last_time)
                        current_false += 1
                    else:
                        falsetime = max(timedelta(0),current_time - last_time)
                current_val = line[2]
                last_time = current_time
            else:
                idx_copy = idx
                while idx < len(cars[current_car]) and current_time - cars[current_car][idx][1] > timedelta(minutes=5):
                    idx = idx + 1
                if idx < len(cars[current_car]):
                    #print "here",last_time,current_time,cars[current_car][idx_copy][1]
                    #print cars[current_car][idx_copy][1], last_time
                    if current_val == 't':
                        truetime += max(timedelta(0), cars[current_car][idx_copy][1] - last_time)
                    else:
                        falsetime += max(timedelta(0), cars[current_car][idx_copy][1] - last_time)
                    if timediff > timedelta(0):
                        print current_true,current_false,timediff.total_seconds(),truetime.total_seconds(),falsetime.total_seconds()
                        drivers[cars[current_car][idx_copy][2]][0] += truetime.total_seconds()
                        drivers[cars[current_car][idx_copy][2]][1] += falsetime.total_seconds()
                        timediff = timedelta(0)
                        truetime = timedelta(0)
                        falsetime = timedelta(0)
                        current_true = 0
                        current_false = 0
                    if cars[current_car][idx][0] - current_time > timedelta(minutes=5):
                        last_time = cars[current_car][idx][0]
                        continue
                    else:
                        current_car = line[0]
                        current_val = line[2]
                        last_time = current_time
                        #print "set time 3"
                        if current_val == 't':
                            current_true = 1
                            current_false = 0
                        else:
                            current_false = 1
                            current_true = 0
                else:
                    if current_val == 't':
                        truetime += max(timedelta(0), cars[current_car][idx_copy][1] - last_time)
                    else:
                        falsetime += max(timedelta(0), cars[current_car][idx_copy][1] - last_time)
                    if timediff > timedelta(0):
                        print current_true,current_false,timediff.total_seconds(),truetime.total_seconds(),falsetime.total_seconds()
                        drivers[cars[current_car][idx_copy][2]][0] += truetime.total_seconds()
                        drivers[cars[current_car][idx_copy][2]][1] += falsetime.total_seconds()
                        timediff = timedelta(0)
                        truetime = timedelta(0)
                        falsetime = timedelta(0)
                        current_false = 0
                        current_true = 0
        elif line[0] != current_car and line[0] in cars:
            print "car changed"
            idx_copy = idx-1
            v = 0
            if cars[line[0]][v][0] - current_time >= timedelta(minutes=5):
                print current_time,cars[line[0]][v][0]
                continue
            else:
                print "looping"
                while v < len(cars[line[0]]) and current_time - cars[line[0]][v][1] > timedelta(minutes=5):
                    v = v + 1
                if v < len(cars[line[0]]):
                    if cars[line[0]][v][0] - current_time >= timedelta(minutes=5):
                        continue
                    else:
                        if current_val == 't':
                            truetime += max(timedelta(0), cars[current_car][idx_copy][1] - last_time)
                        else:
                            falsetime += max(timedelta(0), cars[current_car][idx_copy][1] - last_time)
                        if timediff > timedelta(0):
                            print current_true,current_false,timediff.total_seconds(),truetime.total_seconds(),falsetime.total_seconds()
                            drivers[cars[current_car][idx_copy][2]][0] += truetime.total_seconds()
                            drivers[cars[current_car][idx_copy][2]][1] += falsetime.total_seconds()
                        current_car = line[0]
                        current_val = line[2]
                        last_time = current_time
                        #print "set time 3"
                        if current_val == 't':
                            current_true = 1
                            current_false = 0
                        else:
                            current_false = 1
                            current_true = 0
                        timediff = timedelta(0)
                        truetime = timedelta(0)
                        falsetime = timedelta(0)
                        idx = v
                else:
                    if current_val == 't':
                        truetime += max(timedelta(0), cars[current_car][idx_copy][1] - last_time)
                    else:
                        falsetime += max(timedelta(0), cars[current_car][idx_copy][1] - last_time)
                    if timediff > timedelta(0):
                        print current_true,current_false,timediff.total_seconds(),truetime.total_seconds(),falsetime.total_seconds()
                        drivers[cars[current_car][idx_copy][2]][0] += truetime.total_seconds()
                        drivers[cars[current_car][idx_copy][2]][1] += falsetime.total_seconds()
                        timediff = timedelta(0)
                        truetime = timedelta(0)
                        falsetime = timedelta(0) 
                
    if current_car in cars:
        if current_val == 't':
            truetime += max(timedelta(0), cars[current_car][min(idx,len(cars[current_car])-1)][1] - last_time)
        else:
            falsetime += max(timedelta(0), cars[current_car][min(idx,len(cars[current_car])-1)][1] - last_time)
    print current_true,current_false,timediff.total_seconds(),truetime.total_seconds(),falsetime.total_seconds()
    drivers[cars[current_car][min(idx,len(cars[current_car])-1)][2]][0] += truetime.total_seconds()
    drivers[cars[current_car][min(idx,len(cars[current_car])-1)][2]][1] += falsetime.total_seconds()

for driver in drivers:
    print driver,drivers[driver][0]/(drivers[driver][0]+drivers[driver][1]),drivers[driver][1]/(drivers[driver][0]+drivers[driver][1])

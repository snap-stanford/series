from datetime import datetime
from datetime import timedelta
import sys

cars = {}
with open('/dfs/scratch0/dataset/vw/tsv_sorted/sessions.tsv') as fp:
    for line in fp:
        line = line.strip().split('\t')
        if line[0] not in cars:
            cars[line[0]] = []
        cars[line[0]].append((datetime.strptime(line[1],"%Y-%m-%d %H:%M:%S.%f"),datetime.strptime(line[2],"%Y-%m-%d %H:%M:%S.%f")))

if len(sys.argv) < 2:
    print "Usage : <script> <filename>"
    exit(0)

fname = sys.argv[1]
with open('/dfs/scratch0/dataset/vw/tsv_sorted/'+fname) as fp:
    current_car = ""
    idx = 0
    current_true = 0
    current_false = 0
    current_val = 't'
    timediff = timedelta(0)
    last_time = None
    for line in fp:
        line = line.strip().split('\t')
        current_time = datetime.strptime(line[1],"%Y-%m-%d %H:%M:%S.%f")
        if current_car == "":
            current_car = line[0]
            current_val = line[2]
            last_time = current_time
            if line[2] == 't':
                current_true = 1
            else:
                current_false = 1
        if line[0] == current_car and line[0] in cars and idx < len(cars[current_car]) and current_time >= cars[current_car][idx][0] and (idx + 1 == len(cars[current_car]) or current_time < cars[current_car][idx+1][0]) and line[2] != current_val:
            if current_time <= cars[current_car][idx][1]:
                timediff += current_time - last_time
                if line[2] == 't':
                    current_true += 1
                else:
                    current_false += 1
                current_val = line[2]
                last_time = current_time
        elif line[0] != current_car and line[0] in cars and current_time >= cars[line[0]][0][0] and (1 == len(cars[line[0]]) or current_time < cars[line[0]][1][0]):
            print current_true,current_false,timediff.total_seconds()
            current_car = line[0]
            current_val = line[2]
            last_time = current_time
            if current_val == 't':
                current_true = 1
                current_false = 0
            else:
                current_false = 1
                current_true = 0
            timediff = timedelta(0)
            idx = 0
        elif current_car in cars and idx + 1 < len(cars[current_car]) and current_time >= cars[current_car][idx+1][0]:
            idx = idx + 1
            if current_time <= cars[current_car][idx][1]:
                print current_true,current_false,timediff.total_seconds()
                current_car = line[0]
                current_val = line[2]
                last_time = current_time
                if current_val == 't':
                    current_true = 1
                    current_false = 0
                else:
                    current_false = 1
                    current_true = 0
                timediff = timedelta(0)
    print current_true,current_false,timediff.total_seconds()




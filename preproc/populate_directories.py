import os
from datetime import datetime
import sys

if len(sys.argv) < 2:
    print "USAGE : <script> <sensor name>"
    exit(0)

location = '/lfs/local/0/abhisg/vw/hour_data_2/'
sensor = sys.argv[1]

#pointers = {}
#for name in os.listdir(location):
#    if os.path.isdir(location+name):
#        pointers[name] = ''
#        #pointers[name] = open(location+name+'/'+sensor,'w+')

with open('/dfs/scratch0/dataset/vw/tsv_sorted/'+sensor) as fp:
    for line in fp:
        data = line.strip().split('\t')
        current_folder_name = datetime.strftime(datetime.strptime(data[1],"%Y-%m-%d %H:%M:%S.%f"),"%Y%m%d_%H")
        print current_folder_name
        try:
            pointer = open(location+current_folder_name+'/'+sensor,'w+')
            pointer.write(line)
            pointer.close()
        except:
            continue
        

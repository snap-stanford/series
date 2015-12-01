import os, sys
import numpy as np

clusters = []
MAX_LATLNG = 0.0004
MAX_DIR = 20

# cluster turns
def turn_cluster():
    for filename in os.listdir('/dfs/scratch0/silei/vw_project/turns/'):
        driver_id, sid, lat, lng, d_before, d_after = filename.split('_')
        driver_id = int(driver_id)
        lat = float(lat)
        lng = float(lng)
        d_before = int(d_before)
        d_after = int(d_after)
        turn = [driver_id, lat, lng, d_before, d_after, filename]

        clustered = False
        for i in range(0, len(clusters)):
            if in_cluster(clusters[i], turn):
                clusters[i].append(turn)
                clustered = True
                break
        if clustered == False:
            clusters.append([turn])


# check whether a turn belongs to a cluster
def in_cluster(cluster, turn):
    if abs(cluster[0][1] - turn[1]) <= MAX_LATLNG and \
       abs(cluster[0][2] - turn[2]) <= MAX_LATLNG and \
       abs(cluster[0][3] - turn[3]) <= MAX_DIR and \
       abs(cluster[0][4] - turn[4]) <= MAX_DIR:
        return True
    else:
        return False

# output large clusters
def output(threshold = 100):
    f = open('clusters_%d' %threshold, 'w')
    latlngs = open('latlngs_%d' %threshold, 'w')
    
    for cluster in clusters:
        size = len(cluster)
        if size > threshold:
            for turn in cluster:
                f.write(str(turn[0]) + ' ')
                f.write(str(turn[1]) + ' ')
                f.write(str(turn[2]) + ' ')
                f.write(str(turn[3]) + ' ')
                f.write(str(turn[4]) + '\t')
                with open(os.path.join('/dfs/scratch0/silei/vw_project/turns/', turn[-1]), 'r') as f_turn:
                    lines = f_turn.readlines()
                    line = lines[50].split('\t')
                    latlngs.write('new GLatLng(%s, %s), ' %(line[4], line[5]))
                    line = lines[-50].split('\t')
                    latlngs.write('new GLatLng(%s, %s), ' %(line[4], line[5]))
                #latlngs.write('new GLatLng(%f, %f), ' %(turn[1], turn[2]))
            f.write('\n')
            latlngs.write('\n')
    f.close()
    latlngs.close()

# output filenames in each cluster
# each line contains filenames in one cluster separated by tab
def output_filenames():
    with open('clusters', 'w') as f:
        for cluster in clusters:
            for turn in cluster:
                f.write(str(turn[-1]) + '\t')
            f.write('\n')

# output the avg value for each cluster
def output_avg():
    f = open('avg', 'w')
    clusters.sort(lambda x, y: -cmp(len(x), len(y)))
    for cluster in clusters:
        f.write(str(len(cluster)) + '\t') 
        avg_value = get_avg(cluster)
        for i in range(4):
            f.write(str(avg_value[i]) + '\t')
        f.write('\n')
    f.close()
        

# get avg value for a cluster
def get_avg(cluster):
    avg_value = [0.0, 0.0, 0.0, 0.0]
    for turn in cluster:
        for i in range(4):
            avg_value[i] += turn[i + 1] 
    return [v / len(cluster) for v in avg_value]
        

if __name__ == '__main__':
    turn_cluster()
    output_filenames()
    output()
    output_avg()

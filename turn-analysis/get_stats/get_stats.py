import os, sys
import pandas as pd
from datetime import datetime
from math import sin, asin, sqrt, cos, sqrt, radians, isnan
from id import get_driver_keys, get_car_keys

Time = dict()
Dist = dict()

def distance(loc1, loc2):
    lat1, lng1 = loc1
    lat2, lng2 = loc2
    lng1, lat1, lng2, lat2 = map(radians, [lng1, lat1, lng2, lat2])
    # haversine formula 
    dlng = lng2 - lng1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlng/2)**2
    c = 2 * asin(sqrt(a)) 
    km = 6371 * c
    return km

def get_sessions():
    driver_keys = get_driver_keys()
    car_keys = get_car_keys()
    sessions = dict()
    with open('../stats/sessions.tsv', 'r') as f:
        for line in f:
            contents = line.split('\t')
            driver_id = contents[-1].rstrip()
            if driver_id != '__EMPTY__':
                driver_key = driver_keys[driver_id]
                car_key = car_keys[contents[0]]
                num_session = contents[-2]
                sid = '%02d%03d' %(int(car_key), int(num_session))
                sessions[sid] = driver_key 
    return sessions

sessions = get_sessions()

for i, filename in enumerate(os.listdir('../snapshots')):
    print filename

    # get user id from file name
    _, ckey, nsession = filename.split('_') 
    if int(ckey) == 3 and int(nsession[:-4]) <= 32:
        continue
    sid = '%02d%03d' %(int(ckey), int(nsession[:-4]))
    uid = sessions[sid]

    fil = os.path.join('../snapshots/', filename)
    # filter out empty files
    filsize = os.path.getsize(fil)  
    if filsize < 1024:
        continue
    
    # calculate driving time for the session
    with open(fil, 'r') as f:
        # get second line in snapshot file
        f.readline()
        second = f.readline()
        # get last line in snapshot file
        f.seek(-2, 2)
        while f.read(1) != '\n':
            f.seek(-2, 1)
        last = f.readline()

        # extract start time and end time
        t_start = second.split('\t')[0]
        t_end = last.split('\t')[0]
        format = '%Y-%m-%d %H:%M:%S.%f'
        t_start = datetime.strptime(t_start, format)
        t_end = datetime.strptime(t_end, format)  

        # get time in hours
        time =  (t_end - t_start).total_seconds() / 60.0 / 60.0

    # calculate driving distance for the session   
    df = pd.read_csv(fil, header = None, delim_whitespace = True)
    df.columns = ['Day', 'Time', 'Steer_Angle', 'Velocity', 'Heading', 'Latitude', 'Longitude', 'Brightness', 'Road_Type', 'Num_Oncoming_Lanes', 'Curr_Seg_ID', 'Seg_Dist_Left', 'Next_Seg_ID', 'Steer_Velocity', 'Brake', 'Pedal', 'Fuel', 'X_Accel', 'Y_Accel', 'Mileage', 'RPM', 'Wiper_Speed', 'Time2Coll', 'Deacc_Request', 'L_Sig', 'R_Sig']
    
    lat = df['Latitude']
    lng = df['Longitude']
    length = len(df)

    # skip 1st line, store the location in 2nd line as 'previous location'
    # and starts from the 3rd line
    pre_loc = [lat[1], lng[1]]
    dist = 0.0
    for i in range(2, length):
        loc = [lat[i], lng[i]]
        d = distance(pre_loc, loc)
        if d > 0.1:
            pass
            #print dist, lat[i], lng[i]
        else:
            dist += d
        pre_loc = loc

    print dist
    
    if uid in Time:
        Time[uid].append(time)
        #if not isnan(dist):
        Dist[uid].append(dist)
    else:
        Time[uid] = [time]
        #if not isnan(dist):
        Dist[uid] = [dist]

with open('stats_time', 'w') as f:
    total_time = 0.0
    num_session = 0
    for uid in sorted(Time):
        f.write(str(uid) + '\t')
        f.write(str(len(Time[uid])) + '\t')
        f.write(str(sum(Time[uid])) + '\t')
        f.write(str(sum(Time[uid])/len(Time[uid])) + '\n')
        total_time += sum(Time[uid])
        num_session += len(Time[uid])
    f.write(str(num_session/64.0) + '\t')
    f.write(str(num_session) + '\t')
    f.write(str(total_time/64.0) + '\t')
    f.write(str(total_time) + '\t')

with open('stats_distance', 'w') as f:
    total_dist = 0.0
    num_session = 0
    for uid in sorted(Dist):
        f.write(str(uid) + '\t')
        f.write(str(len(Dist[uid])) + '\t')
        f.write(str(sum(Dist[uid])) + '\t')
        f.write(str(sum(Dist[uid])/len(Dist[uid])) + '\n')
        total_dist += sum(Dist[uid])
        num_session += len(Dist[uid])
    f.write(str(num_session/64.0) + '\t')
    f.write(str(num_session) + '\t')
    f.write(str(total_dist/64.0) + '\t')
    f.write(str(total_dist) + '\t')

        





	





	

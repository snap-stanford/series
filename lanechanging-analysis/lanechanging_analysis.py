import os 
import pandas as pd

sum = 0
sum_signal = 0
path = '/dfs/scratch0/silei/vw_project/lane_changings4'
for i, filname in enumerate(os.listdir(path)):
    fil = os.path.join(path, filname)
    df = pd.read_csv(fil, header = None, delim_whitespace = True)
    df.columns = ['Day', 'Time', 'Steer_Angle', 'Velocity', 'Heading', \
            'Latitude', 'Longitude', 'Brightness', 'Road_Type', \
            'Num_Oncoming_Lanes', 'Curr_Seg_ID', 'Seg_Dist_Left', \
            'Next_Seg_ID', 'Steer_Velocity', 'Brake', 'Pedal', 'Fuel', \
            'X_Accel', 'Y_Accel', 'Mileage', 'RPM', 'Wiper_Speed', \
            'Time2Coll', 'Deacc_Request', 'L_Sig', 'R_Sig']

    # record of last 5 seconds
    sum += 1
    for i in range(len(df)):
        if df['L_Sig'][i] == 't' or df['R_Sig'][i] == 't':
            sum_signal += 1
            break

print float(sum_signal) / sum


import os
import pandas as pd
import datetime
import csv
import math

fil = '/dfs/scratch0/silei/vw_project/snapshots/snapshots_2_55.dat'

def str_to_sec(time):
    format = '%Y-%m-%d %H:%M:%S.%f'
    time = datetime.datetime.strptime(time, format)
    sec = float(time.strftime('%s.%f'))
    return sec

# detect lane changing by observing the change on steering wheel angle
# max_degree: the maximum degree changing
# min_velocity: the minimum average velocity 
# min_stable: the minimum stable time before and after lane changing (in 0.1s)
# max_time: the maximum time for a lane changing
def detect_lane_changing(fil, max_degree = 10., min_velocity = 30., \
        min_stable = 30, max_change_time = 50, max_heading_change = 10.):
    starts = []
    ends = []

    # skip empty file
    if os.path.getsize(fil) < 1:
        return starts, ends

    df = pd.read_csv(fil, header = None, delim_whitespace = True)
    if df.shape[1] != 26:
        print 'skip file because of insufficient columns: ' + fil
        return starts, ends
    for i in range(0, 26):
        if df[i][0] == '':
            print 'skip file because of empty entry found: ' + fil
            return starts, ends
    df.columns = ['Day', 'Time', 'Steer_Angle', 'Velocity', 'Heading', \
            'Latitude', 'Longitude', 'Brightness', 'Road_Type', \
            'Num_Oncoming_Lanes', 'Curr_Seg_ID', 'Seg_Dist_Left', \
            'Next_Seg_ID', 'Steer_Velocity', 'Brake', 'Pedal', 'Fuel', \
            'X_Accel', 'Y_Accel', 'Mileage', 'RPM', 'Wiper_Speed', \
            'Time2Coll', 'Deacc_Request', 'L_Sig', 'R_Sig']

    # record of last 5 seconds
    # initialize heading direction's record by [0, 180, 0, 180,...], so that 
    # it's unstable until it's filled up
    heading_prev = [0, 180] * (min_stable / 2)
    steering_prev = [0] * min_stable
    avg_heading = 0
    start = end = -1
    status = 'unstable'
    
    for i in range(0, len(df)):
        heading_prev[i % min_stable] = df['Heading'][i]
        steering_prev[i % min_stable] = df['Steer_Angle'][i]

        # if road type is not free way, continue to next iteration
        if int(df['Road_Type'][i]) != 5:
            status = 'unstable'
            continue

        #print fil

        # state 'stable', ready to detect lane changing
        if status == 'stable':
            # if the headng direction is still stable, just update avg_heading
            if is_stable(heading_prev):
                avg_heading = avg_direction(heading_prev)
                # if the steering angle changes
                steering_change = changes(steering_prev, i, min_stable)
                if steering_change == 1:
                    status = 'positive change'
                    start = i
                elif steering_change == -1:
                    status = 'negative change'
                    start = i
            # if the heading direction is not stable
            # update status to 'unstable'
            else:
                status = 'unstable'

        # state 'positve/negative change'
        elif status.endswith('change'):
            # if max_change_time exceeded since the change start
            # quit recording
            if i - start > max_change_time:
                status = 'unstable'
                continue
            if status == 'positive change':
                if changes(steering_prev, i, min_stable) == -1:
                    status = 'change back'
            else:
                if changes(steering_prev, i, min_stable) == 1:
                    status = 'change back'

        # state 'change back'
        elif status == 'change back':
            # if max_change_time exceeded since the change start
            # quit recording
            if i - start > max_change_time:
                status = 'unstable'
                continue
            #if diff_direction(avg_heading, avg_direction(df['Heading'][i: max(len(df), i + min_stable)]))\
            #if diff_direction(avg_heading, avg_direction(heading_prev))\
            if diff_direction(avg_heading, heading_prev[i % min_stable])\
                    < max_heading_change:
                if changes(steering_prev, i, min_stable) == 0 and is_stable(heading_prev):
                    end = i
                    starts.append(max(0, start - 10))
                    ends.append(min(end, len(df)))
                    status = 'stable'
            else:
                status = 'unstable'

        # state 'unstable', waiting for becoming 'stable' 
        else: 
            if is_stable(heading_prev):
                status = 'stable'
                avg_heading = avg_direction(heading_prev)
            
    return starts, ends

# detect steering wheel angle change
# return 1 if a positive change is detected 
# return -1 if a negative change is detected 
def changes(steering_list, index, min_stable, min_threshold = 5, max_threshold = 60, \
        min_time = 10):
    sum_positive = 0
    sum_negative = 0
    sum_angle = 0.0
    for i in range(min_time):
        sum_angle += steering_list[(index - i) % min_stable]
        if steering_list[(index - i) % min_stable] > 0:
            sum_positive += 1
        elif steering_list[(index - i) % min_stable] < 0:
            sum_negative += 1
    avg_angle = sum_angle / min_time
    if sum_positive == 10 and avg_angle > min_threshold \
            and avg_angle < max_threshold:
        return 1
    elif sum_negative == 10 and avg_angle < - min_threshold \
            and avg_angle > - max_threshold:
        return -1
    return 0 


# given a list of heading directions (0~360), check whether its stable
# i.e., whether the heading direction is within a range, say 20 degree
# note that 0, 360 are towards to the same direction, so cannot just 
# use 'max-min' to solve this
def is_stable(heading_list, threshold = 10.):
    length = len(heading_list)
    minimum = maximum = heading_list[0]
    diff = lambda x, y: min(abs(x-y), abs(abs(x-y)-360))
    for i in range(1, length):
        direction = heading_list[i]
        # print minimum, maximum, direction
        if diff(minimum, direction) > threshold:
            return False
        elif diff(maximum, direction) > threshold:
            return False
        else:
            if direction > maximum:
                maximum = direction
            if direction < minimum:
                minimum = direction
    return True


# given a list of heading directions (0~360), return the average heading
# direction. note that 0, 360 are towards the same direction, so cannot
# just use the average value of list
def avg_direction(heading_list):
    length = len(heading_list)
    # dividing each direaction into x-axis, y-axis two parts
    xaxis = []
    yaxis = []
    for degree in heading_list:
        # math.cos and math.sin use angle in radians, not degree
        radian = math.radians(degree)
        xaxis.append(math.cos(radian))
        yaxis.append(math.sin(radian))
    avg_x = sum(xaxis) / float(len(xaxis))
    avg_y = sum(yaxis) / float(len(yaxis))
    # math.atan return value in radians, not degree
    avg_direction = math.degrees(math.atan2(avg_y, avg_x))
    if avg_direction < 0:
        return 360 + avg_direction
    return avg_direction

# given two heading direction (0, 360), return the difference between 
# these two direction
def diff_direction(dir1, dir2):
    diff_num = abs(dir1 - dir2)
    return min(diff_num, 360 - diff_num)

def avg_velocity(velocity_list):
    return sum(velocity_list) / len(velocity_list)


if __name__ == '__main__':
    detect_lane_changing(fil)

    

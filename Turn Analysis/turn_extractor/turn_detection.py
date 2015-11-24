import datetime
import csv
import math

filename = '../snapshots/snapshots_2_55.dat'

def str_to_sec(time):
    format = '%Y-%m-%d %H:%M:%S.%f'
    time = datetime.datetime.strptime(time, format)
    sec = float(time.strftime('%s.%f'))
    return sec

# detect the turning by observing the data of angle of steering wheel
# along with the speed
def detect_turning_by_steeringwheel(filename):
    starts = []
    ends = []
    status = ''
    # record the speed in last 5 seconds
    velocity_list = [0] * 50
    # record the absolute value of steering wheel angle in last 2 seconds
    angle_list = [0] * 20
    with open(filename, 'r') as f:
        for i, line in enumerate(f):
            contents = line.split('\t')
            angle = float(contents[1])
            velocity = float(contents[2])
            
            # maintain the reconds
            velocity_list[i%50] = velocity
            angle_list[i%20] = abs(angle)

            # only consider turning when last 5 seconds, the max speed is 20 miles on more
            if status != 'turning' and abs(angle) > 40 and max(velocity_list) > 30:
                #print angle, max(velocity_list)
                #print velocity_list
                status = 'turning'
                starts.append(max(0, i - 80))
            elif status == 'turning' and max(angle_list) < 10:
                status = ''
                ends.append(i + 20)

    # remove start point with no ending point
    while len(starts) != len(ends):
        starts.pop()

    return starts, ends


# detect the turning by observing the change on heading direction 
# along with the speed
# min_degree: the minimum degree required for a turning
# min_velocity: the minimum average velocity required before turning and 
#    the minimum average velocity required during turning is half of it
# min_stable: the minimum stable time before turning (in 0.1s)
# max_turning_time: the maximum time for a turning
def detect_turning_by_heading(filename, min_degree = 70., min_velocity = 20., min_stable = 50,\
        max_turning_time = 100.):
    starts = []
    ends = []

    with open(filename, 'r') as f:
        # get velocity list and heading direction list from column 2 and 3 
        contents = csv.reader(f, delimiter = '\t')
        contents_t = zip(*contents)
        if len(contents_t) < 5:
            print 'warning: skip file since less than 5 columns in ' + filename
            return starts, ends
        for i in range(0, len(contents_t) - 1):
            if contents_t[i][0] == '':
                print 'warning: skip file since empty entry found in file ' + filename
                return starts, ends
        velocity_list = [float(i) for i in contents_t[2]]
        heading_list = [float(i) for i in contents_t[3]]

    # record of last 5 seconds
    # initialize heading direction's record by [0, 180, 0, 180,...], so that 
    # it's unstable until it's filled up
    velocity_prev = [0] * min_stable
    heading_prev = [0, 180] * (min_stable / 2)
    avg_heading = 0
    turning_start = turning_end = -1
    status = 'unstable'
    
    for i in range(0, len(velocity_list)):
        velocity_prev[i % min_stable] = velocity_list[i]
        heading_prev[i % min_stable] = heading_list[i]
        if status == 'stable':
            # if the headng direction is still stable, just update avg_heading
            if is_stable(heading_prev):
                avg_heading = avg_direction(heading_prev)
            # if the heading direction is not stable, and the average speed in
            # last 5 seconds is larger than min_velocity requirement. then
            # update status to 'turning' and record the turning start time
            #elif avg_velocity(velocity_prev) > min_velocity:
            elif avg_velocity(velocity_prev) > min_velocity:
                status = 'turning'
                turning_start = i
            else:
                status = 'unstable'
        elif status == 'turning':
            # if the the heading direction is stable again after 'turining'
            # check whether current avg_heading is different from avg_heading
            # before turning
            if is_stable(heading_prev):
                avg_now = avg_direction(heading_prev)
                # if avg_now - avg_heading larger than minimum degree for a 
                # turning, record the turning
                if diff_direction(avg_now, avg_heading) > min_degree:
                    turning_end = i
                    # if the turning last for more than 10s, filter it out
                    if turning_end - turning_start < max_turning_time + 50 and \
                            turning_end - turning_start > 50 and avg_velocity(velocity_list[turning_start:turning_end-50]) > min_velocity / 2.0:
                        #print turning_end - turning_start
                        starts.append(max(0, turning_start - 50))
                        ends.append(min(turning_end, len(velocity_list))) 
                # update avg_heading, and wait for new turning
                avg_heading = avg_now
                status = 'stable'

        # state 'unstable'
        else: 
            if is_stable(heading_prev):
                status = 'stable'
                avg_heading = avg_direction(heading_prev)
            else:
                pass
            
    return starts, ends


# given a list of heading directions (0~360), check whether its stable
# i.e., whether the heading direction is within a range, say 20 degree
# note that 0, 360 are towards to the same direction, so cannot just 
# use 'max-min' to solve this
def is_stable(heading_list, threshold = 20.):
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
    #print detect_turning_by_heading(filename)
    #print detect_turning_by_steeringwheel(filename)
    test = [98.200000000000003, 98.200000000000003, 98.200000000000003, 98.200000000000003, 98.200000000000003, 98.200000000000003, 98.200000000000003, 98.200000000000003, 98.200000000000003, 52.100000000000001, 52.100000000000001, 52.100000000000001, 52.100000000000001, 52.100000000000001, 52.100000000000001, 52.100000000000001, 52.100000000000001, 52.100000000000001, 52.100000000000001, 359.69999999999999, 359.69999999999999, 359.69999999999999, 359.69999999999999, 359.69999999999999, 359.69999999999999, 359.69999999999999, 359.69999999999999, 359.69999999999999, 359.69999999999999, 312.10000000000002, 312.10000000000002, 312.10000000000002, 312.10000000000002, 312.10000000000002, 312.10000000000002, 312.10000000000002, 312.10000000000002, 312.10000000000002, 312.10000000000002, 274.30000000000001, 274.30000000000001, 274.30000000000001, 274.30000000000001, 274.30000000000001, 274.30000000000001, 274.30000000000001, 274.30000000000001, 274.30000000000001, 274.30000000000001, 266.89999999999998]
    print avg_direction(test)
    print is_stable(test)

    

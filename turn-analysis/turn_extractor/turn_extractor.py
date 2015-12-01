import sys, os
from turn_detection import * 

dict_sessions = dict()

# extract turns from filenames given the start_lines and end_lines of turns
# where no line overlapping exists for all turns.
# the output files are named as follows
# [Session_ID]_[Lat]_[Lng]_[Avg_Heading_before_turn]_[Avg_Heading_after_turn]
# where session_id is [Driver_KEY][Car_KEY][Session_num]
def turn_extractor(filename, start_line, end_line):
    dir = '/dfs/scratch0/silei/vw_project/snapshots/'
    fil = os.path.join(dir, filename)
    sid = get_session_id(filename)
    num_turns = len(start_line)
    with open(fil, 'r') as f:
        j = 0
        heading = []
        lat = []
        lng = []
        lines = []
        for i, line in enumerate(f):
            if j >= num_turns:
                break
            if i <= end_line[j]:
                if i >= start_line[j]:
                    contents = line.split('\t')
                    heading.append(float(contents[3]))
                    lat.append(float(contents[4]))
                    lng.append(float(contents[5]))
                    lines.append(line)
            else:
                output(sid, heading, lat, lng, lines)
                j = j + 1
                heading = []
                lat = []
                lng = []
                lines = []

# split start_line and end_line lists so that there's no overlappings lines for turns
# in each sublist, 
# so that we can read the file for a couple of times to get all turns out.
def turn_extractor_all(filename, start_line, end_line):
    starts = [[], []]
    ends = [[], []]
    for i in range(0, len(start_line)):
        starts[i%2].append(start_line[i])
        ends[i%2].append(end_line[i])
    for i in range(0, len(starts)):
        turn_extractor(filename, starts[i], ends[i])


# output a turn 
def output(sid, heading, lat, lng, lines):
    heading_before = avg_direction(heading[:50])
    heading_after = avg_direction(heading[-50:])
    center = len(lat) / 2
    clat = lat[center]
    clng = lng[center]
    suffix = '_%.6f_%.6f_%03d_%03d' % (clat, clng, heading_before, heading_after)
    dir = '/dfs/scratch0/silei/vw_project/turns/'
    fil = os.path.join(dir, sid + suffix)
    with open(fil, 'w') as f:
        for line in lines:
            f.write(line)


# generate sessions dictionary, where key is [Car_KEY][Session_num], 
# value is [Driver_KEY]
def get_session_dict():
    with open('/dfs/scratch0/silei/vw_project/stats/driver_sessions', 'r') as f:
        for line in f:
            contents = line.strip().split('\t')
            driver_key = contents[0]
            sessions = contents[2:]
            for session in sessions:
                ckey, nsession = session.split()
                key = '%02d%03d' %(int(ckey), int(nsession))
                dict_sessions[key] = driver_key
                

# get session id by filename
def get_session_id(filename):
    _, ckey, nsession = filename.split('_')
    ckey = int(ckey)
    nsession = int(nsession[:-4])
    key = '%02d%03d' %(ckey, nsession)
    dkey = '%02d' %int(dict_sessions[key])
    return dkey + '_' + key
    


# main function to process data
def extract_turns(filename):
    get_session_dict()
    dir = '/dfs/scratch0/silei/vw_project/snapshots/'
    snapshot = os.path.join(dir, filename)
    starts, ends = detect_turning_by_heading(snapshot)
    turn_extractor_all(filename, starts, ends)


if __name__ == '__main__':
    extract_turns(sys.argv[1])
    

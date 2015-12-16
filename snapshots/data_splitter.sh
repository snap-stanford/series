import os, sys

from id import *

# get the session id by car_key and session number
# session_id is defined as 5-digit number where first 2 digits represents 
# car_key and last 3 digit represents session number
def get_session_id(car_key, num_session):
    return '%02d%03d' %(int(car_key), int(num_session))

# mkdir for each session
def mkdir():
    # dict: keys -- car_ids, values -- car_keys
    car_keys = get_car_keys()
    with open('../stats/sessions.tsv', 'r') as f:
        for line in f:
            contents = line.split('\t')
            driver_id = contents[-1].rstrip()
            if driver_id != '__EMPTY__':
                car_key = car_keys[contents[0]]
                num_session = contents[-2]
                dir = os.path.join('../data/', get_session_id(car_key, num_session))
                if not os.path.isdir(dir):
                    os.mkdir(dir)

def get_linenumber(filename):
    session_id = []
    start_line = []
    end_line = []
    with open(os.path.join('../stats/linenumbers', filename), 'r') as f:
        for line in f:
            ckey, dkey, nsession, sline, eline = line.split('\t')
            session_id.append(get_session_id(ckey, nsession))
            start_line.append(int(sline))
            end_line.append(int(eline))
    return session_id, start_line, end_line

# split file by sessions
#######################################################
# for each session, save one line before that session
# but don't save one line after the session
#######################################################
def splitter(filename):
    if filename.endswith('_values.tsv'):
        return 0
    session_id, start_line, end_line = get_linenumber(filename)
    session_num = len(session_id)
    index = 0

    dir_original = '/dfs/scratch0/dataset/vw/tsv_sorted/'
    f_original = open(os.path.join(dir_original, filename), 'r')

    long_time_ago = '\t2000-01-01 00:00:00.000000\t'
    prev_line = ''
    prev_carid = ''
    started = False
    for i, line in enumerate(f_original):
        if index >= session_num:
            break
        #print i, session_id[index], started
        contents = line.split('\t')
        if len(contents) != 3:
            print 'wrong format in line %d of file %s' %(i, file)
            return 0
        carid = contents[0]
        value = contents[-1].rstrip()
        if carid != prev_carid:
            prev_line = carid + long_time_ago + get_prev_value(value) + '\n'
        if started == False and i > start_line[index]:
            f = open(new_file(filename, session_id[index]), 'w')
            ################################
            # need to consider the case prev_line = ''
            #if prev_line == '':
                #prev_line = carid + long_time_ago + get_prev_value(value) + '\n'
            f.write(prev_line)
            f.write(line)
            started = True
            while index < session_num and i == end_line[index]:
                f.close()
                f = open(new_file(filename, session_id[index]), 'w')
                f.write(prev_line)
                f.close()
                index += 1
                started = False
            if started == False and index < session_num and start_line[index] == i-1:
                f = open(new_file(filename, session_id[index]), 'w')
                f.write(prev_line)
                f.write(line)
                started = True
        elif started == True and i < end_line[index]:
            f.write(line)
        elif started == True and i == end_line[index]:
            f.close()
            started = False
            index += 1
            # go though all the cases that
            # start_line = i - 1 and end_line = i
            while index < session_num and i == end_line[index]:
                f = open(new_file(filename, session_id[index]), 'w')
                f.write(prev_line)
                f.close()
                index += 1
            if index < session_num and start_line[index] == i-1:
                f = open(new_file(filename, session_id[index]), 'w')
                f.write(prev_line)
                f.write(line)
                started = True
        elif started == True:
            print 'SHIT'
        prev_line = line
        prev_carid = carid

    # hit the end of the file or all sessions have been processed
    if index < session_num and started == True:
        f.close()
        index += 1
    while index < session_num:
        f = open(new_file(filename, session_id[index]), 'w')
        f.write(prev_line)
        f.close() 
        index += 1

    f_original.close()

# return directory+file of splitted data based on filename and session id
def new_file(filename, sid):
    dir_new = '/dfs/scratch0/silei/vw_project/data/'
    file = os.path.join(dir_new, sid, sid + filename)
    return file

# when previous value is not available, generate the previous value 
# based on current value
def get_prev_value(value):
    if value.replace('.', '', 1).replace('-', '', 1).isdigit():
        prev_value = value
    else:
        if value == 't':
            prev_value = 'f'
        elif value == 'f':
            prev_value = 't'
        else:
            print '######################'
            print [value]
            return ''
    return prev_value


if __name__ == '__main__':
    mkdir()
    #splitter('s_motor_18_mo_startstopp_popup.tsv')
    if len(sys.argv) < 2:
        print 'wrong format!' 
        print 'format: data_splitter.py filename1 filename2 ...'
    else:
        for i in range(1, len(sys.argv)):
            splitter(sys.argv[i])



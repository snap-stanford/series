import sys, os
import time, datetime
from id import *
from timetransfer import *

#sys.stdout = open('log', 'w')

# get informations from sessions.tsv
def get_sessions():
    car_id = []
    time_start = []
    time_end = []
    sessions = []
    driver_id = []
    with open('../stats/sessions.tsv', 'r') as f:
        for i, line in enumerate(f):
            contents = line.split('\t')
            if contents[4].rstrip() != '__EMPTY__':
                car_id.append(contents[0])
                time_start.append(str_to_sec(contents[1]))
                time_end.append(str_to_sec(contents[2]))
                sessions.append(contents[3])
                driver_id.append(contents[4].rstrip())
    return car_id, time_start, time_end, sessions, driver_id


# get information from sessions.tsv, in format of 5 lists 
car_id, time_start, time_end, sessions, driver_id = get_sessions()
car_key = car_ids_to_keys(car_id)
driver_key = driver_ids_to_keys(driver_id)
car_dict = get_car_keys()


# extract the line number of each driving time session for the entire dataset 
# and print them out in the file with the same name in 'linenumber' folder
def extract_linenumbers():
    data_path = '/dfs/scratch0/dataset/vw/tsv_sorted/'
    #data_path = '../data/'

    for filename in os.listdir(data_path):

        # if the the file has already been processed, skip the file
        if os.path.isfile('../stats/linenumbers/' + filename) and \
                os.path.getsize('../stats/linenumbers/' + filename) > 10240:
            print filename + ' has been processed, skip it'
            continue
        
        file = os.path.join(data_path, filename)
        if not checkfile(file):
            continue

        # start processing file
        print 'processing ' + filename

        # initialize parameters
        index = 0
        started = False
        start_line = -1
        linenumber = -1
        time = 0.0
        ckey = -1
        eof = False
        length = len(car_id)
        
        fin = open(file, 'r')
        fout = open('../stats/linenumbers/' + filename, 'w+')
        #fout = open(filename, 'w')

        index = -1
        while index < length - 1:
            index += 1

            if eof:
                if started == True:
                    fout.write(str(linenumber + 1) + '\n')
                    started = False
                fout.write(car_key[index] + '\t')
                fout.write(driver_key[index] + '\t')
                fout.write(sessions[index] + '\t')
                fout.write(str(start_line) + '\t')
                fout.write(str(linenumber + 1) + '\n')
                continue

            # new car id is different from the recorded cid
            ##################################
            while ckey != car_key[index]:
                line = fin.readline()
                if not line:
                    eof = True
                    break
                else:
                    ckey, time = get_ckey_time(line)
                    linenumber += 1
            ##################################

            while not eof:
                # new cid is different from the current car id (car_id[index])
                ##################################
                if ckey != car_key[index]:
                    if started == True:
                        fout.write(str(linenumber) + '\n')
                        started = False
                    else:
                        fout.write(car_key[index] + '\t')
                        fout.write(driver_key[index] + '\t')
                        fout.write(sessions[index] + '\t')
                        fout.write(str(start_line) + '\t')
                        fout.write(str(linenumber) + '\n')
                    while index + 1 < length and car_key[index + 1] != ckey:
                        index += 1
                        fout.write(car_key[index] + '\t')
                        fout.write(driver_key[index] + '\t')
                        fout.write(sessions[index] + '\t')
                        fout.write(str(start_line) + '\t')
                        fout.write(str(linenumber) + '\n')
                    break
                ##################################

                if started == False:
                    if time < time_start[index]:
                        start_line = linenumber
                        line = fin.readline()
                        if not line:
                            eof = True
                            break
                        else:
                            ckey, time = get_ckey_time(line)
                            linenumber += 1
                    elif time <= time_end[index]:
                        start_line = linenumber - 1
                        fout.write(car_key[index] + '\t')
                        fout.write(driver_key[index] + '\t')
                        fout.write(sessions[index] + '\t')
                        fout.write(str(start_line) + '\t')
                        start_line = linenumber
                        started = True
                        line = fin.readline()
                        if not line:
                            eof = True
                            break
                        else:
                            ckey, time = get_ckey_time(line)
                            linenumber += 1
                    else:
                        fout.write(car_key[index] + '\t')
                        fout.write(driver_key[index] + '\t')
                        fout.write(sessions[index] + '\t')
                        fout.write(str(start_line) + '\t')
                        fout.write(str(linenumber) + '\n')
                        break
                else:
                    if time <= time_end[index]:
                        start_line = linenumber
                        line = fin.readline()
                        if not line:
                            eof = True
                            break
                        else:
                            ckey, time = get_ckey_time(line)
                            linenumber += 1
                    else:
                        fout.write(str(linenumber) + '\n')
                        started = False
                        break

        if started == True:
            fout.write(str(linenumber + 1) + '\n')

        fin.close()
        fout.close()
        print 'finish processing ' + filename
    return True


# get car key and time from a line
def get_ckey_time(line):
    cid, time, _ = line.split('\t')
    if cid in car_dict:
        ckey = car_dict[cid]
    else:
        ckey = -1
    time = str_to_sec(time)
    return ckey, time


# check the file format for processing
def checkfile(file):
    # skip '*_values.tsv' files
    if file.endswith('_values.tsv'):
        return False
    # check file format, if the file does not contain 3 columns, skip
    with open(file, 'r') as f:
        num_cols = len(f.readline().split('\t'))
        if num_cols != 3:
            print 'wrong format, skip ' + file
            return False
    return True


# get the start and end linenumber in a file for a given time session
def get_linenumber(car_key, time_session, filename):
    car_key = str(car_key)
    time_session = str(time_session)
    with open('../stats/linenumbers/' + filename, 'r') as f:
        for line in f:
            ckey, _, session, line_start, line_end = line.split('\t')
            if session == time_session and car_key == ckey:
                return int(line_start), int(line_end)
    print 'wrong car key and time session pair!'
    return -1, -1


# main
if __name__ == '__main__':
    start_time = time.time()
    extract_linenumbers()
    end_time = time.time()
    print end_time - start_time


            

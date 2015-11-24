# extract snapshots of given sensors in the given time session
# time session is determined by the car id and #time session from sessions.tsv

import os, sys
from time import time
from datetime import datetime, timedelta
from extract_linenumbers import get_linenumber
from extract_linebreaks import get_line_offset
from id import *


# filename list 
# DON'T CHANGE THIS
filenames = ['s_lwi_01_lwi_lenkradwinkel.tsv', 's_kombi_01_kbi_angez_geschw.tsv',\
             's_navdata_01_nd_heading.tsv']
# CHANGE THIS
#filenames += ['s_navpos_01_np_latdegree.tsv', 's_navpos_01_np_longdegree.tsv']
filenames += [\
             's_navpos_01_np_latdegree.tsv', 's_navpos_01_np_longdegree.tsv',\
             's_rls_01_ls_helligkeit_ir.tsv',\
             's_psd_02_psd_sys_strklassen_erweitert.tsv',\
             's_psd_02_psd_sys_fahrsp_gegenr.tsv', \
             's_psd_01_psd_pos_segment_id.tsv', \
             's_psd_01_psd_pos_segmentlaenge.tsv', \
             's_psd_01_psd_segment_id.tsv', \
             's_lwi_01_lwi_lenkradw_geschw.tsv',\
             's_esp_05_esp_bremsdruck.tsv',\
             's_motor_20_mo_fahrpedalrohwert_01.tsv',\
             's_kombi_02_kbi_inhalt_tank.tsv',\
             's_esp_02_esp_laengsbeschl.tsv',\
             's_esp_02_esp_querbeschleunigung.tsv',\
             's_kombi_02_kbi_kilometerstand.tsv',\
             's_motor_12_mo_drehzahl_01.tsv',\
             's_wischer_01_wischer1_wischgeschwindigkeit.tsv',\
             's_acc_10_pcf_time_to_collision.tsv',\
             's_acc_10_anb_zielbrems_teilbrems_verz_anf.tsv'\
             ]
# DON'T CHANGE THIS
filenames += ['s_gateway_72_bh_blinker_li.tsv', 's_gateway_72_bh_blinker_re.tsv']

dir = '/dfs/scratch0/dataset/vw/tsv_sorted'

# car key: 0 - 9
car_keys = range(0, 10)
# time session: 1 - #total number
time_sessions_list = [range(1, 299), range(1, 80), range(1, 221), range(1, 271),\
        range(1, 126), range(1, 251), range(1, 290), range(1, 174), \
        range(1, 293), range(1, 277)]

# interval (in microseconds) of snapshots
INTERVAL = 100000

# car key to id dictionary
car_ids = get_car_ids()


# given the car_key, and time_session number, find the id of the car and 
# time session (start time, end time)
def get_time_session(car_key, time_session):
    car_id = get_car_id(car_key)
    with open('../stats/sessions.tsv', 'r') as sessions:
        for line in sessions:
            id, time_start, time_end, session, driver = line.split('\t')
            if int(session) == int(time_session):
                if id == car_id:
                    if driver.rstrip() == '__EMPTY__':
                        print 'driving session with no driver info, skip'
                        return -1, -1
                    format = '%Y-%m-%d %H:%M:%S.%f'
                    time_start = datetime.strptime(time_start, format)
                    time_end = datetime.strptime(time_end, format)
                    return time_start, time_end

    print 'error: cannot find time session!'
    return -1, -1


# generate an empty table (dict) given the start time and end time
def get_empty_table(time_start, time_end, interval=INTERVAL):
    table = dict()

    # sec_start, the first time point after start time which is a multiple of interval
    sec_start = float(time_start.strftime('%s.%f'))
    sec_start = int(sec_start * (1000000 / interval) + 1) / float(1000000 / interval)
    # sec_end, the last time point before end time which is a multiple of interval
    sec_end = float(time_end.strftime('%s.%f'))
    sec_end = int(sec_end * (1000000 / interval)) / float(1000000 / interval)

    time_start = datetime.fromtimestamp(sec_start)
    time_end = datetime.fromtimestamp(sec_end)

    time = time_start
    while time <= time_end:
        table[time] = []
        time = time + timedelta(microseconds = interval)
    return table


# print the table to output_file, delimiter = '\t'
def print_table(table, output_file):
    format = '%Y-%m-%d %H:%M:%S.%f'
    with open(output_file, 'w') as o:
        for time in sorted(table):
            o.write(time.strftime(format) + '\t')
            for value in table[time]:
                o.write(str(value) + '\t')
            o.write('\n')


# fill the blanks in the table based on the value ahead or behind
# i = length of value in table - 1
def filled(table, i, prev_value):
    # fill blanks others
    sorted_table = sorted(table)
    for iter, time in enumerate(sorted_table):
        #print i, len(table[time])
        if len(table[time]) != i + 1:
            table[time].append(prev_value)
        elif table[time][i] == 'NaN':
            table[time][i] = prev_value
        else:
            prev_value = table[time][i]
        #print i, len(table[time])
    # if there are '' in the table at the beginning
    foll_value = 'NaN'
    for time in sorted_table:
        #print i, len(table[time])
        if table[time][i] != 'NaN':
            foll_value = table[time][i]
            break
    if not foll_value.replace('.', '', 1).replace('-', '', 1).isdigit():
        if foll_value == 'f':
            foll_value = 't'
        elif foll_value == 't':
            foll_value = 'f'
    for time in sorted_table:
        if table[time][i] == 'NaN':
            table[time][i] = foll_value
        else:
            break
    return table


# extract snapshots in format of dict where key is the time and value is list of values
# extracted from the given list of files.
def extract_snapshots(filenames, car_key, time_session, interval=INTERVAL):
    #print car_key, time_session

    car_id = car_ids[car_key]

    time_start, time_end = get_time_session(car_key, time_session)
    if time_start == -1 and time_end == -1:
        return False

    table = get_empty_table(time_start, time_end, interval)

    # update time_start to 0.1s ealier to make sure that we get the very first
    # 0.1s timestamp after time start
    sec_start = float(time_start.strftime('%s.%f')) - 0.1
    time_start = datetime.fromtimestamp(sec_start)

    for j, filename in enumerate(filenames):
        file = os.path.join(dir, filename)
        # start is the line before start line
        # end is the line after end line
        start, end = get_linenumber(car_key, time_session, filename)
        #print j, start, end
        num_lines = end - start - 1
        with open(file, 'r') as f:
            # go to start line
            if start == -1:
                offset = get_line_offset(filename, start + 1)
                prev_value = 'NaN'
            else:
                offset = get_line_offset(filename, start)
                f.seek(offset)
                cid, timestamp, value = f.readline().split('\t')
                # store the values before the start time
                # will be none if there's no previous value (i.e., in time session 1)
                if cid == car_id:
                    prev_value = value.rstrip()
                else:
                    prev_value = 'NaN'
            for i, line in enumerate(f):
                if i < num_lines:
                    #print i, num_lines
                    id, time, value = line.split('\t') 
                    value = value.rstrip()
                    format = '%Y-%m-%d %H:%M:%S.%f'
                    time = datetime.strptime(time, format)
                    if time > time_end:
                        break
                    elif time < time_start:
                        prev_value = value
                    elif time >= time_start:
                        sec = round(float(time.strftime('%s.%f')), 1)
                        time = datetime.fromtimestamp(sec)
                        if time in table:
                            if len(table[time]) == j:
                                table[time].append(value)
                else:
                    break
        # fill blanks in table
        table = filled(table, j, prev_value)
    return table
                    
def generate_snapshots(filenames, car_key, time_sessions):
    for time_session in time_sessions:
        file = '../snapshots/snapshots2_' + str(car_key) + '_' + str(time_session) + '.dat'
        if os.path.isfile(file):
            print 'file exists, skip snapshots_' + str(car_key) + '_' + str(time_session)
            continue
        start_time = time()
        table = extract_snapshots(filenames, car_key, time_session)
        if table != False:
            print_table(table, file)
        end_time = time()
        print end_time - start_time
                    
def generate_snapshots_per_session(filenames, car_key, time_session):
    file = '../snapshots/snapshots_' + str(car_key) + '_' + str(time_session) + '.dat'
    if os.path.isfile(file):
        print 'file exists, skip snapshots_' + str(car_key) + '_' + str(time_session)
        return 0
    #start_time = time()
    table = extract_snapshots(filenames, car_key, time_session)
    if table != False:
        print_table(table, file)
    #end_time = time()
    #print end_time - start_time

if __name__ == '__main__':
    generate_snapshots_per_session(filenames, sys.argv[1], sys.argv[2])

    #for i in range(0, len(car_keys)):
    #    generate_snapshots(filenames, car_keys[i], time_sessions_list[i])



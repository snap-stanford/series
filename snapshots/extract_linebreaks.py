import sys, os
import time

INTERVAL = 10000

# extract the line breaks for the entire dataset and print them out with the 
# same file name in 'linebreaks' folder
# interval: store offset of every 1000 line break as default
def extract_linebreaks(interval = INTERVAL):
    data_path = '/dfs/scratch0/dataset/vw/tsv_sorted/'
    #data_path = './test_data/'

    for filename in os.listdir(data_path):
        # skip '*_values.tsv' files
        if filename.endswith('_values.tsv'):
            pass
        # main func
        else:
            file = os.path.join(data_path, filename) 
            # check file format, if the file does not contain 3 columns, skip
            with open(file, 'r') as fcheck:
               num_cols = len(fcheck.readline().split('\t'))
               if num_cols != 3:
                   print 'wrong format, skip ' + file
                   continue
            # start processing file
            print 'processing ' + filename
            with open(file, 'r') as fin:
                with open('../stats/linebreaks/' + filename, 'w') as fout:
                    line_offset = []
                    offset = 0
                    for i, line in enumerate(fin):
                        if i % interval == 0:
                            line_offset.append(offset)
                        offset += len(line)
                    for number in line_offset:
                        fout.write(str(number) + '\n')
            print 'finish processing ' + filename
    return True


# load the line breaks of a given file by a list
def load_linebreaks(filename):
    data_path = '../stats/linebreaks'
    file = os.path.join(data_path, filename)
    list_linebreaks = []
    with open(file, 'r') as f:
        for line in f:
            list_linebreaks.append(int(line))
    return list_linebreaks


# get line given the line number
# line number starts from 0
def get_line(filename, num_line, interval = INTERVAL):
    index = num_line / interval
    remainder = num_line % interval
    list_linebreaks = load_linebreaks(filename)
    data_path = '/dfs/scratch0/dataset/vw/tsv_sorted/'
    file = os.path.join(data_path, filename)
    with open(file, 'r') as f:
        f.seek(list_linebreaks[index])
        for i in range(-1, remainder):
            line = f.readline()
        return line

# get the offset of the last linebreak before a given line
def get_line_offset(filename, num_line, interval = INTERVAL):
    index = num_line / interval
    remainder = num_line % interval
    list_linebreaks = load_linebreaks(filename)
    offset = list_linebreaks[index]
    data_path = '/dfs/scratch0/dataset/vw/tsv_sorted/'
    file = os.path.join(data_path, filename)
    with open(file, 'r') as f:
        f.seek(offset)
        for i in range(0, remainder):
            line = f.readline()
            offset += len(line)
    return offset
            

if __name__ == '__main__':
    # main 
    start_time = time.time()
    extract_linebreaks()
    end_time = time.time()
    print end_time - start_time

    # test
    #start_time = time.time()
    #filename = 's_motor_12_mo_drehzahl_01.tsv'
    #data_path = '/dfs/scratch0/dataset/vw/tsv_sorted/'
    #file = os.path.join(data_path, filename)
    #offset = get_line_offset(filename, 999999)
    #with open(file, 'r') as f:
    #    f.seek(offset)
    #    print f.readline()
    #end_time = time.time()  
    #print end_time - start_time


            

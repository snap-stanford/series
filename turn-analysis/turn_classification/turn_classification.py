import os, sys
import pandas as pd
import numpy as np
#import cpickle as pickle
import pickle

from sklearn.cluster import KMeans
from sklearn.preprocessing import scale
from time import time

#sys.stdout = open('log', 'w')

TURNS_PATH = '/dfs/scratch0/silei/vw_project/turns/'
NUM_CLUSTER = 5

# extract feature vector for a given file
def extract_feature_vector(filename):
    feature_vector = []
    fil = os.path.join(TURNS_PATH, filename)
    df = pd.read_csv(fil, header = None, delim_whitespace = True)
    df.columns = ['Day', 'Time', 'Steer_Angle', 'Velocity', 'Heading', \
            'Latitude', 'Longitude', 'Brightness', 'Road_Type', \
            'Num_Oncoming_Lanes', 'Curr_Seg_ID', 'Seg_Dist_Left', \
            'Next_Seg_ID', 'Steer_Velocity', 'Brake', 'Pedal', 'Fuel', \
            'X_Accel', 'Y_Accel', 'Mileage', 'RPM', 'Wiper_Speed', \
            'Time2Coll', 'Deacc_Request', 'L_Sig', 'R_Sig']

    key_columns = ['Steer_Angle', 'Velocity', 'Brake', 'Pedal', \
            'X_Accel', 'Y_Accel']

    # cacluate mean, max, min for each 'key_index'
    feature_vector.append(len(df))
    for col in key_columns:
        # status: before turn, turning, after turn
        status = [df[col][:50], df[col][50:-50], df[col][-50:]]
        for s in status:
            feature_vector.append(sum(s) / len(s))
            feature_vector.append(max(s))
            feature_vector.append(min(s))
    return feature_vector

# extract feature vectors for all files, and save to file
def extract_feature_matrix():
    fmat = []
    fils = []
    for i, filename in enumerate(sorted(os.listdir(TURNS_PATH))):
        #print i, filename
        fvec = extract_feature_vector(filename)
        fmat.append(fvec)
        fils.append(filename)
    fmat = np.array(fmat)
    with open('feature_matrix.pkl', 'wb') as handle:
        pickle.dump(fmat, handle)
    with open('filenames.pkl', 'wb') as handle:
        pickle.dump(fils, handle)
    return fmat

# k means clustering
def kmeans(feature_matrix, k):
    km = KMeans(n_clusters = k, init = 'k-means++', max_iter = 100, n_init = 1)
    new_fmat = scale(feature_matrix)
    km.fit(new_fmat)
    #km.fit(feature_matrix)
    return km

# get list of filenames in specific label
def get_files(label, labels):
    with open('filenames.pkl', 'rb') as handle:
        fils = pickle.load(handle)
    indices = [i for i, l in enumerate(labels) if l == label]
    return [fils[i] for i in indices]

# get avg vector value for turns with specific label
def get_avg_vector(label, labels, feature_matrix):
    indices = [i for i, l in enumerate(labels) if l == label]
    sum = [0.0] * feature_matrix.shape[1]
    for i in indices:
        sum += feature_matrix[i]
    return sum / len(indices)

# check the whether a turn is indicated by signal
def signal_check(filename):
    fil = os.path.join(TURNS_PATH, filename)
    df = pd.read_csv(fil, header = None, delim_whitespace = True)
    df.columns = ['Day', 'Time', 'Steer_Angle', 'Velocity', 'Heading', \
            'Latitude', 'Longitude', 'Brightness', 'Road_Type', \
            'Num_Oncoming_Lanes', 'Curr_Seg_ID', 'Seg_Dist_Left', \
            'Next_Seg_ID', 'Steer_Velocity', 'Brake', 'Pedal', 'Fuel', \
            'X_Accel', 'Y_Accel', 'Mileage', 'RPM', 'Wiper_Speed', \
            'Time2Coll', 'Deacc_Request', 'L_Sig', 'R_Sig']
    length = len(df) / 2
    for i in range(0, length):
        if df['L_Sig'][i] == 't' or df['R_Sig'][i] == 't':
            return True
    return False

# check all turns 
def signal_check_all():
    signal_record = dict()
    for filename in os.listdir(TURNS_PATH):
        signal_record[filename] = signal_check(filename)
    with open('signal_record.pkl', 'wb') as handle:
        pickle.dump(signal_record, handle)
    return signal_record

# main func
def main():
    # if .pkl file exisit, load it, otherwise run matrix extracting function
    if os.path.isfile('feature_matrix.pkl'):
        with open('feature_matrix.pkl', 'rb') as handle:
            feature_matrix = pickle.load(handle) 
    else:
        feature_matrix = extract_feature_matrix()

    # if .pkl file exisit, load it, otherwise run signal check function
    if os.path.isfile('signal_record.pkl'):
        with open('signal_record.pkl', 'rb') as handle:
            signal_record = pickle.load(handle) 
    else:
        signal_record = signal_check_all()

    #for k in [4, 6, 8, 10, 15, 20]:
    #    km = kmeans(feature_matrix, k)
    #    print km.inertia_

    km = kmeans(feature_matrix, NUM_CLUSTER)
    #print km.cluster_centers_
    #print km.labels_
    #print km.inertia_

    # print out the size of each cluster and the avg value of each cluster
    size = [0.0] * NUM_CLUSTER
    for label in km.labels_:
        size[label] += 1
    print 'Size of clusters: ' + str(size).strip('[]')
    print 'Average value of turns in each cluster: '
    for label in range(0, NUM_CLUSTER):
        print get_avg_vector(label, km.labels_, feature_matrix)


    # print out the percentage of siganl using for each cluster
    num_turn_no_signal = [0] * NUM_CLUSTER
    num_turn_signal = [0] * NUM_CLUSTER
    for label in range(0, NUM_CLUSTER):
        fils = get_files(label, km.labels_)
        for fil in fils:
            signal = signal_record[fil]
            if signal:
                num_turn_signal[label] += 1
            else:
                num_turn_no_signal[label] += 1
    
    for i in range(0, NUM_CLUSTER):
        print float(num_turn_signal[i]) / (num_turn_signal[i] + num_turn_no_signal[i])


if __name__ == '__main__':
    main()

import cPickle as pickle
import numpy as np
from sklearn.cross_validation import StratifiedShuffleSplit
from sklearn import preprocessing
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from scipy import stats
from collections import Counter
from sklearn.metrics import confusion_matrix
import sys

#features = pickle.load(open('../DataForClassification_V_last.pkl'))
if len(sys.argv) < 7:
	print "File user1 user2 user3 user4 user5"
	exit(0)
features = pickle.load(open(sys.argv[1]))
#features = pickle.load(open('../data/DataForClassification_final_simple_cross_longer_48.7880144539_11.3811151809_178.508532423_91.2866894198.pkl'))
X = []
Y = []
#users = {4:[],6:[],10:[],12:[],15:[],35:[],45:[],50:[]}
#classif = {4:[],6:[],10:[],12:[],15:[],35:[],45:[],50:[]}
#labels = [10,6,21,45,50]
labels = map(int,[sys.argv[i] for i in xrange(2,7)])
print labels
#labels = [12,10,6,57,54]
#labels = [6,10,45,35,12]
#labels = [6,10]
users = {}
classif = {}
trials = 100
classifiers = [[] for i in xrange(trials)]
for user in labels:
	users[user] = [[] for i in xrange(trials)]
	classif[user] = [[] for i in xrange(trials)]
test_X = []
test_Y = []
np.random.seed(1)
for j in [0]:
	data = np.array(features)
	idx = []
	for i in xrange(len(data)):
		if data[i,-1] in users.keys():
			idx.append(i)
	idx = np.array(idx)
	data_X = data[idx,:-1]
	data_X = data_X[:,allindices]
	data_Y = data[idx,-1]
	freq = dict(Counter(data_Y))
	mincount = min(freq.values())
	print Counter(data_Y)
	idx = []
	for user in users.keys():
		idx = idx + np.random.permutation(np.where(data_Y==user)[0])[:mincount].tolist()
		#idx = idx + (np.where(data_Y==user)[0])[:mincount].tolist()
	idx = np.array(idx)
	data_X = data_X[idx]
	data_Y = data_Y[idx]
	#cvobj = StratifiedShuffleSplit(data_Y,n_iter=trials)
	cvobj = StratifiedShuffleSplit(data_Y,n_iter=trials,test_size=len(users))
	#model = RandomForestClassifier(oob_score=True,n_estimators=1000,warm_start=False,class_weight='auto',random_state=123,max_features="auto")
	model = RandomForestClassifier(n_estimators=1000,max_features=0.66,random_state=123,n_jobs=-1,class_weight='auto')
	actual,predictions = [],[]
	#model = LogisticRegression(random_state=1,class_weight='auto')
	for train_idx,test_idx in cvobj:
		model.fit(data_X[train_idx,:],data_Y[train_idx])
		actual = actual + data_Y[test_idx].tolist()
		predictions = predictions + model.predict(data_X[test_idx,:]).tolist()
		"""classifiers[ctr].append(model)
		seen = []
		for idx in test_idx:
			userid = int(data_Y[idx])
			if userid not in seen:
				seen.append(userid)
				#classif[userid][ctr].append(model.predict_proba(data_X[idx]))
				classif[userid][ctr].append(model.predict(data_X[idx]))"""
print confusion_matrix(actual,predictions,labels)
#pickle.dump(classif,open('classification_results_6_10_V3_random.pkl','w+'))

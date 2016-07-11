import cPickle as pickle
import numpy as np
import itertools
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

data = np.array(features)
idx = []
for i in xrange(len(data)):
	if data[i,-1] in users.keys():
		idx.append(i)
idx = np.array(idx)
data_X = data[idx,:-1]
data_Y = data[idx,-1]
freq = dict(Counter(data_Y))
mincount = min(freq.values())
print Counter(data_Y)
for i in xrange(2,6):
	importance = np.zeros(data_X.shape[1],)
	print importance.shape
	res,counter = 0,0
	#for combo in itertools.combinations(users.keys(),i):
	combo = [v[0] for v in Counter(data_Y).most_common(i)]
	#for combo in freq.most_common(i):
	idx = []
	for user in combo:
		#idx = idx + np.random.permutation(np.where(data_Y==user)[0])[:mincount].tolist()
		idx = idx + (np.where(data_Y==user)[0])[-mincount:].tolist()
	idx = np.array(idx)
	Xdata = data_X[idx]
	Ydata = data_Y[idx]
	#cvobj = StratifiedShuffleSplit(data_Y,n_iter=trials)
	cvobj = StratifiedShuffleSplit(Ydata,n_iter=trials,test_size=len(combo))
	model = RandomForestClassifier(oob_score=True,n_estimators=1000,warm_start=False,class_weight='auto',random_state=123,max_features="auto")
	#model = RandomForestClassifier(n_estimators=1000,max_features=0.66,random_state=123,n_jobs=-1,class_weight='auto')
	actual,predictions = [],[]
	#model = LogisticRegression(random_state=1,class_weight='auto')
	for train_idx,test_idx in cvobj:
		model.fit(Xdata[train_idx,:],Ydata[train_idx])
		importance += model.feature_importances_
		actual = actual + Ydata[test_idx].tolist()
		predictions = predictions + model.predict(Xdata[test_idx,:]).tolist()
	#print np.argsort(importance)[::-1][:20]
	res,counter = res + np.mean(np.array(actual) == np.array(predictions)),counter+1
	print combo
	print confusion_matrix(actual,predictions)
	print "Mean for",i,res*1./counter
	print "Importance for",i,np.argsort(importance)[::-1][:20]
#pickle.dump(classif,open('classification_results_6_10_V3_random.pkl','w+'))

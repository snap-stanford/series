from cvxpy import *
import cPickle as pickle
import numpy as np
import json
from sklearn.cross_validation import StratifiedShuffleSplit

features = pickle.load(open('DataForOpt_V3.pkl'))
X = []
Y = []
labels = []
for i in xrange(8):
	X.append(Variable(3))
for i in xrange(7):
	Y.append(Variable(3))
featurelist = []
users = {4:0,6:1,10:2,12:3,15:4,35:5,45:6,50:7}
for j in xrange(7):
	for i in xrange(len(features[j])):
		userid = users[int(features[j][i][-1])]
		featurelist.append(features[j][i].tolist()+[j])
		labels.append((userid,j))

features = np.array(featurelist)
cvobj = StratifiedShuffleSplit(labels)
lambdas = [0.01,0.05,0.1,0.25,0.5,1,5,10,25,50,100]
#minerror,minarr = 100000000,[]
"""trainerrors,testerrors = {},{}
for l in lambdas:
	trainerror,testerror = [],[]
	for train_idx,test_idx in cvobj:
		trainerrormat,testerrormat = np.zeros((8,7)),np.zeros((8,7))
		expr = ""
		train_features,test_features = features[train_idx],features[test_idx]
		for i in xrange(train_features.shape[0]):
			turnid,userid = int(train_features[i][-1]),users[int(train_features[i][-2])]
			if i == 0:
				expr = square(norm(Y[turnid]+X[userid]-train_features[i,np.array([0,4,5])].reshape(3,1))) + l*norm(X[userid])
			else:
				expr = expr + square(norm(Y[turnid]+X[userid]-train_features[i,np.array([0,4,5])].reshape(3,1))) + l*norm(X[userid])
		prob = Problem(Minimize(expr))
	   	prob.solve(verbose=False)
		print prob.value
		for i in xrange(train_features.shape[0]):
			turnid,userid = int(train_features[i][-1]),users[int(train_features[i][-2])]
			#print turnid,userid,(np.subtract(Y[turnid].value+X[userid].value,train_features[i,np.array([0,4,5])].reshape(3,1))).shape
			trainerrormat[userid][turnid] += np.linalg.norm(Y[turnid].value+X[userid].value-train_features[i,np.array([0,4,5])].reshape(3,1))**2
		for i in xrange(test_features.shape[0]):
			turnid,userid = int(test_features[i][-1]),users[int(test_features[i][-2])]
			testerrormat[userid][turnid] += np.linalg.norm(Y[turnid].value+X[userid].value-test_features[i,np.array([0,4,5])].reshape(3,1))**2
		trainerror.append(np.sum(np.sum(trainerrormat))/train_features.shape[0])
		testerror.append(np.sum(np.sum(testerrormat))/test_features.shape[0])
		print trainerror,testerror
	trainerrors[l] = np.mean(trainerror)
	testerrors[l] = np.mean(testerror)
	print l,"is done with errors",trainerrors[l],testerrors[l]
json.dump(trainerrors,open('training_errors.json','w+'))
json.dump(testerrors,open('test_errors.json','w+'))
"""

l = 1
testerrormat = np.zeros((8,7))
testerrormatcount = np.ones((8,7))
for train_idx,test_idx in cvobj:
	trainerrormat,testerrormat = np.zeros((8,7)),np.zeros((8,7))
	expr = ""
	train_features,test_features = features[train_idx],features[test_idx]
	for i in xrange(train_features.shape[0]):
		turnid,userid = int(train_features[i][-1]),users[int(train_features[i][-2])]
		if i == 0:
			expr = square(norm(Y[turnid]+X[userid]-train_features[i,np.array([0,4,5])].reshape(3,1))) + l*norm(X[userid])
		else:
			expr = expr + square(norm(Y[turnid]+X[userid]-train_features[i,np.array([0,4,5])].reshape(3,1))) + l*norm(X[userid])
	prob = Problem(Minimize(expr))
	prob.solve(verbose=False)
	print prob.value
	for i in xrange(test_features.shape[0]):
		turnid,userid = int(test_features[i][-1]),users[int(test_features[i][-2])]
		testerrormat[userid][turnid] += np.linalg.norm(Y[turnid].value+X[userid].value-test_features[i,np.array([0,4,5])].reshape(3,1))**2
		testerrormatcount[userid][turnid] += 1
print np.divide(testerrormat,testerrormatcount)

"""expr = ""
for j in xrange(7):
	for i in xrange(len(features[j])):
		userid = users[int(features[j][i][-1])]
		if j == 0 and i == 0:
			expr = square(norm(Y[j]+X[userid]-features[j][i][np.array([0,4,5])])) + 0.01*norm(X[userid])
	  	else:
			expr = expr + square(norm(Y[j]+X[userid]-features[j][i][np.array([0,4,5])])) + 0.01*norm(X[userid])
prob = Problem(Minimize(expr))
prob.solve(verbose=True)
print prob.value
for i in xrange(len(Y)):
	Y[i] = Y[i].value
for i in xrange(len(X)):
	X[i] = X[i].value
print "\tTurn1 Turn2 Turn3 Turn4 Turn5 Turn6 Turn7"
print "Avg",Y[0][0],Y[1][0],Y[2][0],Y[3][0],Y[4][0],Y[5][0],Y[6][0]
print "Max",Y[0][1],Y[1][1],Y[2][1],Y[3][1],Y[4][1],Y[5][1],Y[6][1]
print "Min",Y[0][2],Y[1][2],Y[2][2],Y[3][2],Y[4][2],Y[5][2],Y[6][2]


print "\tDriver1 Driver2 Driver3 Driver4 Driver5 Driver6 Driver7 Driver 8"
print "Avg",X[0][0],X[1][0],X[2][0],X[3][0],X[4][0],X[5][0],X[6][0],X[7][0]
print "Max",X[0][1],X[1][1],X[2][1],X[3][1],X[4][1],X[5][1],X[6][1],X[7][1]
print "Min",X[0][2],X[1][2],X[2][2],X[3][2],X[4][2],X[5][2],X[6][2],X[7][2]"""

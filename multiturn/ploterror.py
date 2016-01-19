import matplotlib.pyplot as plt
import json
import numpy as np
train = json.load(open('training_errors.json'))
test = json.load(open('test_errors.json'))
X = sorted(map(float,train.keys()))
training = []
testing = []
print train
for elem in X:
	try:
		training.append(train[str(elem)])
		testing.append(test[str(elem)])
	except:
		training.append(train[str(int(elem))])
		testing.append(test[str(int(elem))])
plt.plot(np.log10(X),training)
plt.plot(np.log10(X),testing)
plt.xlabel('Log lambda')
plt.ylabel('MSE')
plt.legend(['Training','Test'])
plt.show()	

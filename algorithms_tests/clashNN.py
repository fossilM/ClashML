import numpy as np
import scipy as sp
import lasagne
from lasagne import layers
from lasagne.updates import nesterov_momentum
from nolearn.lasagne import NeuralNet
import os

# which approach
appr = int(input("Which approach will you use? 1 or 2?\n"))
if appr == 1:
	M = 33 # number of features plus label for Approach 2 (23) and Approach 1 (33)
	dataFilePath = os.path.abspath('../datasets/approach1_data')
else:
	M = 23  # number of features plus label for Approach 2 (23) and Approach 1 (33)
	dataFilePath = os.path.abspath('../datasets/approach2_data')
	print("ih")

K = int((M - 1) / 2)  # number of features for one player
X_samples_shape = (1, M - 1)  # Dimension of one sample data

trials = 100
accuracy_train = 0
accuracy_test = 0


def load_dataset():
	data = np.loadtxt(dataFilePath, delimiter=',')
	np.random.shuffle(data) #SHUFFLE DATA
	train_perc = 80 #training set percent - Cross Validation
	cross = int((data.shape[0]) * (train_perc/100))

	# LABEL DATA
	Y_train = data[:cross,data.shape[1] - 1]
	Y_train_1 = [0] * cross
	for i in range(cross):
		Y_train_1[i] = (~ int(np.asscalar(Y_train[i]))) + 2
	Y_train = np.concatenate((Y_train,Y_train_1), axis= 0)
	Y_test = data[cross :, data.shape[1] - 1]

	# SAMPLE DATA
	X_data = sp.delete(data, data.shape[1] - 1, axis=1)
	X_train = X_data[:cross]
	X_train_1 = np.copy(X_train)
	for i in X_train_1:
		temp = np.copy(i[:K])
		i[:K] = np.copy(i[K:])
		i[K:] = temp
	X_train = np.concatenate((X_train,X_train_1),axis=0)
	X_test = X_data[cross:]

	#RESHAPE FOR NN ENTRY
	X_train = X_train.reshape(-1,X_samples_shape[0],X_samples_shape[1])
	X_test = X_test.reshape(-1, X_samples_shape[0], X_samples_shape[1])
	Y_train = Y_train.astype(np.uint8)
	Y_test = Y_test.astype(np.uint8)


	return X_train, Y_train, X_test, Y_test


for i in range(trials):

	net1 = NeuralNet(
		layers=[('input', layers.InputLayer),
		        ('dense', layers.DenseLayer),
		        ('dropout2', layers.DropoutLayer),
		        ('output', layers.DenseLayer),
		        ],
		# input layer
		input_shape=(None, 1, X_samples_shape[1]),
		# dense
		dense_num_units=54,
		dense_nonlinearity=lasagne.nonlinearities.rectify,
		# dropout2
		dropout2_p=0.25,
		# output
		output_nonlinearity=lasagne.nonlinearities.softmax,
		output_num_units=2,
		# optimization method params
		update=nesterov_momentum,
		update_learning_rate=0.05,
		update_momentum=0.9,
		max_epochs=250,
		verbose=True
	)

	print('--------- Trial #{} ------------'.format(i))

	X_train, Y_train, X_test, Y_test = load_dataset()
	# Train the network
	nn = net1.fit(X_train, Y_train)

	print("TRAINING DATA ACCURACY")

	preds = net1.predict(X_train)

	score = 0
	#print("TR || P")
	for x,y in zip(Y_train, preds):
		#print(str(x) + "  " + str(y))
		if x == y:
			score+=1

	accuracy_tr = score/len(Y_train)
	accuracy_train += accuracy_tr
	print('{} % \n'.format(accuracy_tr*100))

	print("TEST DATA ACCURACY")

	preds = net1.predict(X_test)

	score = 0
	#print("TS || P")
	for x,y in zip(Y_test,preds):
		#print(str(x) + "  " + str(y))
		if x == y:
			score+=1

	accuracy_ts = score / len(Y_test)
	accuracy_test += accuracy_ts
	print('{} %'.format(accuracy_ts*100))
	print('-------------------------------- \n')

print('TRAINING ACCURACY IS: {} %'.format(str(100 *accuracy_train/trials)))
print('TEST ACCURACY IS: {} %'.format(str(100* accuracy_test/trials)))
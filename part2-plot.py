import tensorflow as tf;
import numpy as np;
import matplotlib.pyplot as plt

def euclidian_distance(x_data,z_data):
  
    xtf = tf.expand_dims(x_data,1); #creates a N1x1xD
    ztf = tf.expand_dims(z_data,0); #creates a 1xN2XD
    
    #show dimensions
    result = xtf - ztf;
    result = result * result;
    result = tf.reduce_sum(result,2); #took out the 2

    return(result);

##########################################################################

#given a dm with the distances with a set of all test and training points

#dm = pairwise distance matrix (n1xn2) of distances between all training points and all test points
# n1 is the number of test points. n2 is the number of training points
# k = number of nearest neighbours you want
#retrun value = a list of the indices of the k nearest neighbours
def responsibility(distanceMatrix, k):
  
    dm = tf.negative(distanceMatrix ); #flip all values to find closest neighbours
 
    #create a responsibility vector   
  
    values, indices = tf.nn.top_k(dm, k);
  
    dmNumCol = dm.shape[1];
    indNumRow = indices.shape[0];

    offsets = tf.range(start = 0, limit = dmNumCol*indNumRow, delta = dmNumCol);
    offsets = tf.expand_dims(offsets, 0);
    offsets = tf.transpose(offsets);

    indices = indices + offsets;
    indices = tf.to_int64(indices);

    flatIndices = tf.reshape(indices, [indices.shape[0]*indices.shape[1]]);
    resVal = tf.constant(1.0,tf.float64)/tf.constant(k,tf.float64);
    flatRes = tf.fill([flatIndices.shape[0]],resVal);
  
    size = dm.shape[0]*dm.shape[1];
  
    ref = tf.Variable(tf.zeros([size],tf.float64));
  
    with tf.Session() as session:
        session.run(tf.global_variables_initializer());
        resVec =  tf.scatter_update(ref,flatIndices, flatRes); 
      
    resVec = tf.reshape(resVec, [distanceMatrix.shape[0], distanceMatrix.shape[1]]);

    return resVec
###########################################################################

#targets = the target value of the test points. a qx1
#responsibility matrix = rxq
#q is the number of test points. r is the number of training points
#result = returns the estimated y values given the responsibility matrix of a 
#set of test points as a col vector

def calculate_predictions(targets, resMat):
    
    
    resMat = tf.cast(resMat, tf.float64)
    targets = tf.cast(targets, tf.float64)
   
    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer());
        
        #print("targets\n", targets);
        #print(sess.run(targets));

        #print("resMat\n", resMat);
        #print(sess.run(resMat[:][1]));
        #print("targets\n", targets);
        
        yhats = tf.matmul(resMat,targets);#multiplies close targets by 1/k and sets others to 0 
        #print("after multiply");
        #print(sess.run(yhats[0:10]));
        #print(yhats);
        
    return(yhats);


############ Original data #################
############################################
np.random.seed(521)
data = np.linspace(1.0, 10.0, num = 100)[:, np.newaxis]
target = np.sin(data) + 0.1*np.power(data,2)+ 0.5 * np.random.randn(100,1)

randIdx = np.arange(100)
np.random.shuffle(randIdx)
trainData, trainTarget = data[randIdx[:80]], target[randIdx[:80]]
validData, validTarget = data[randIdx[80:90]], target[randIdx[80:90]]
testData, testTarget = data[randIdx[90:100]], target[randIdx[90:100]]
############################################

import matplotlib.pyplot as plt
#generates vector X to be used as test data
X = np.linspace(1.0, 10.0, num = 1000)[:, np.newaxis]

#go through all the k values and plot the prediction using X and training data
with tf.Session() as sess:
    k_list = [1,3,5,50]
    #k_list = [1]
    for k_num in k_list:
            x = tf.constant(trainData, tf.float64); #80x1
            z = tf.constant(X, tf.float64); #1000x1 
            
            distance_mat = euclidian_distance(z,x) #using test points in X and training data 
            resMat = responsibility(distance_mat, k_num) 
            sess.run(tf.global_variables_initializer());
            #calculate the prediction using the trainTarget
            X_predictions = calculate_predictions(trainTarget,resMat); 
            
            print("distance mat shape",distance_mat.shape);
            print("X_predictions shape: ", X_predictions.shape)
            print("responsibility matrix shape: ", resMat.shape);
    
            plt.figure(k_num+1) #set scale
            plt.plot(trainData, trainTarget,'.') #both are 80x1  #plot data against target
            
            X_predictions_ = sess.run(X_predictions)
            #print(sess.run(X_predictions));

            plt.plot(X, X_predictions_,'-') #plot X data against X prediction
            plt.title("k-NN regression, k =%d"%k_num)
            plt.show()


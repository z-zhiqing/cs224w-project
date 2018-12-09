#import scikit-learn dataset library
from sklearn import datasets
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import snap
import numpy as np
import datetime
import networkx
from utilities import loadTreesFromFile
from utilities import loadMapping

def classify(features,labels):
#Load dataset
    iris = datasets.load_iris()
    print(iris.target_names)

    # print the names of the four features
    print(iris.feature_names)

    X=data[['sepal length', 'sepal width', 'petal length', 'petal width']]  # Features
    y=data['species']  # Labels

    # Split dataset into training set and test set
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2) # 80% training and 20% test

    clf=RandomForestClassifier(n_estimators=100)

    #Train the model using the training sets y_pred=clf.predict(X_test)
    clf.fit(X_train,y_train)

    y_pred=clf.predict(X_test)

def getFeatures(trees):
    # Root Node degree:
    rootNodes = loadMapping("processed_data/half/half_dfTree_rootNode_mapping.txt")
    rootDegs = []
    for i in rootNodes:
        
    print len(rootNodes)

    ft = pd.DataFrame()
    return ft

if __name__ == "__main__":
    trees = loadTreesFromFile("/Users/zilongwang/Documents/GitHub/cs224w-project/processed_data/half/trees/")
    print len(trees)
    ft = getFeatures(trees)

# -*- coding: utf-8 -*-
"""
Created on Mon Aug 15 10:05:35 2022

@author: thain
"""

# Random Forest -> hyperparameters tuning
#   n_estimators: number of trees in the forest
#   max_features: max number of features considered for splitting a node
#   max_depth: max number of levels in each decision tree
#   min_samples_split: min number of data points placed in a node before the node is split
#   min_samples_leaf: min number of data points allowed in a leaf node
#   booststrap: method for sampling data points

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import RandomizedSearchCV
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedShuffleSplit

#%%
# Dados de entrada:
#   - feaures: Relações espectrais -> x
#   - target: Classes -> y

dataset = pd.read_excel('G:/Outros computadores/Meu modelo Laptop (1)/Documents/Mestrado/decision_tree/features_initial.xlsx',header=0, index_col=0)

X = dataset.iloc[:,1:21].values
y = dataset.iloc[:,0].values

# Dividir os dados em dados de treinamento e de teste:
def validador(x,y):
    validador = StratifiedShuffleSplit(n_splits=1, test_size = 0.25, random_state=0)
    for treino_id, teste_id in validador.split(x,y):
        x_train, x_test = x[treino_id], x[teste_id]
        y_train, y_test = y[treino_id], y[teste_id]
    return x_train, x_test, y_train, y_test

X_train, X_test, y_train, y_test = validador(X,y)

#%%
# METHOD 1 - Random Search

n_estimators = [int(x) for x in np.linspace(start = 200, stop = 2000, num = 10)]
max_features = ['auto', 'sqrt']
max_depth = [int(x) for x in np.linspace(10, 110, num = 11)]
max_depth.append(None)
min_samples_split = [2, 5, 10]
min_samples_leaf = [1, 2, 4]
bootstrap = [True, False]

# Create the random grid
random_grid = {'n_estimators': n_estimators,
               'max_features': max_features,
               'max_depth': max_depth,
               'min_samples_split': min_samples_split,
               'min_samples_leaf': min_samples_leaf,
               'bootstrap': bootstrap}

# Use the random grid to search for best hyperparameters
# First create the base model to tune
rf = RandomForestClassifier()
# Random search of parameters, using 3 fold cross validation, 
# search across 100 different combinations, and use all available cores
rf_random = RandomizedSearchCV(estimator = rf, param_distributions = random_grid, n_iter = 100, cv = 4, verbose=2, random_state=42, n_jobs = -1)
# Fit the random search model
rf_random.fit(X_train,y_train)

print(rf_random.best_params_)

#%%
# METHOD 2 - Grid Search
from sklearn.model_selection import GridSearchCV
# Create the parameter grid based on the results of random search 
param_grid = {
    'bootstrap': [True],
    'max_depth': [15,20,25,30,35,40,45,50,60,70],
    'min_samples_leaf': [1, 2, 3, 4],
    'min_samples_split': [2, 3, 4, 5],
    'n_estimators': [100, 150, 200, 250, 300, 400, 500, 1000, 1500]
}
# Create a based model
rf = RandomForestClassifier(random_state=42)
# Instantiate the grid search model
gs_cv = GridSearchCV(rf, param_grid, scoring = 'balanced_accuracy', cv = 4, verbose=2, n_jobs = -1).fit(X_train, y_train)

# Prints the best parameters
print('Best Hyperparameters %r' % gs_cv.best_params_)
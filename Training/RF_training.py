# -*- coding: utf-8 -*-
"""
Created on Fri Sep  2 10:37:41 2022

@author: thain
"""

# Bibliotecas:
    
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import matplotlib.pyplot as plt
import numpy as np
from sklearn import tree
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
import seaborn as sns

# Dados de entrada:
#   - feaures: Relações espectrais -> x
#   - target: Classes -> y

dataset_train = pd.read_excel('G:/Outros computadores/Meu modelo Laptop (1)/Documents/Mestrado/decision_tree/RF_Train.xlsx',header=0, index_col=0)

X_train = dataset_train.iloc[:,1:7].values
y_train = dataset_train.iloc[:,0].values

dataset_test = pd.read_excel('G:/Outros computadores/Meu modelo Laptop (1)/Documents/Mestrado/decision_tree/RF_Test.xlsx',header=0, index_col=0)

X_test = dataset_test.iloc[:,1:7].values
y_test = dataset_test.iloc[:,0].values

#%%
def executar_classificador(classificador, x_train,y_train,x_test):
    arvore = classificador.fit(x_train, y_train)
    y_pred = arvore.predict(x_test)
    return y_pred

def salvar_arvore(classificador, nome):
  plt.figure(figsize=(200,100))
  tree.plot_tree(classificador, filled=True, fontsize=14)
  plt.savefig(nome)
  plt.close()
  
def validar_arvore(y_test, y_pred):
    aux = []
    accuracy = (accuracy_score(y_test, y_pred))
    precision = (precision_score(y_test, y_pred,pos_label = 1))
    recall = (recall_score(y_test, y_pred,pos_label = 1))
    aux.append(accuracy)
    aux.append(precision)
    aux.append(recall)
    return aux

#%%

model = RandomForestClassifier(bootstrap = True, max_depth = 10, min_samples_leaf = 1, min_samples_split = 2, n_estimators = 300, random_state = 42)
y_pred = executar_classificador(model, X_train, y_train, X_test)

aux = validar_arvore(y_test, y_pred)
salvar_arvore(model.estimators_[0], "G:/Outros computadores/Meu modelo Laptop (1)/Documents/Mestrado/decision_tree/random_forest1")

#%%
#Plot da matriz de confusão

matrix = confusion_matrix(y_test,y_pred)
#matrix = matrix.astype('float') / matrix.sum(axis=1)[:, np.newaxis]

# Build the plot
plt.figure(figsize=(16,9))
sns.set(font_scale=3)
sns.heatmap(matrix, annot=True, annot_kws={'size':75, 'weight':'bold', 'color':'k'}, linecolor='k', linewidths=0.2,cmap="ocean", alpha = 0.3, cbar_kws={'label': 'Samples'})

# Add labels to the plot
class_names = ['No CyHABs', 'CyHABs']
tick_marks = np.arange(len(class_names))
tick_marks2 = tick_marks + 0.5
plt.xticks(tick_marks + 0.5, class_names)
plt.yticks(tick_marks2, class_names)
plt.xlabel('Predicted label', fontsize = 38, weight = 'bold')
plt.ylabel('True label', fontsize = 38, weight = 'bold')
plt.show()

#%%
labels=['Accuracy', 'Precision', 'Recall']
markers = np.linspace(start=0, stop=1, num=6)
str_markers = ["0", "0.2", "0.4", "0.6", "0.8", "1"]
stats = np.array(aux)


labels = np.array(labels)

angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False)
stats = np.concatenate((stats,[stats[0]]))
angles = np.concatenate((angles,[angles[0]]))
labels = np.concatenate((labels,[labels[0]]))

fig = plt.figure(figsize=(15,15))
ax = fig.add_subplot(polar=True)
ax.plot(angles, stats, 'o-', linewidth=2)
ax.fill(angles, stats, alpha=0.25)
ax.set_thetagrids(angles * 180/np.pi, labels)
plt.yticks(markers)
ax.grid(True)

plt.show()

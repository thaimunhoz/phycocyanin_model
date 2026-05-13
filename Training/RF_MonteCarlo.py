# -*- coding: utf-8 -*-
"""
Created on Mon Aug 15 17:22:29 2022

@author: thain
"""

# Bibliotecas:
    
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import matplotlib.pyplot as plt
import numpy as np
from sklearn import tree
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.model_selection import GridSearchCV

# Dados de entrada:
#   - feaures: Relações espectrais -> x
#   - target: Classes -> y

dataset = pd.read_excel('G:/Outros computadores/Meu modelo Laptop (1)/Documents/Mestrado/decision_tree/features_selected.xlsx',header=0, index_col=0)

X = dataset.iloc[:,1:7].values
y = dataset.iloc[:,0].values

X_data = dataset.iloc[:,1:7]

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
  print(accuracy_score(y_test, y_pred))
  print(precision_score(y_test, y_pred))
  print(recall_score(y_test, y_pred))
  print(confusion_matrix(y_test, y_pred))

param_grid = {
    'bootstrap': [True],
    'max_depth': [3,5,10,15,20,25,30,35],
    'min_samples_leaf': [1],
    'min_samples_split': [2],
    'n_estimators': [25,50, 100, 150, 200, 300, 500, 1000]
}
rf = RandomForestClassifier(random_state=42)

#%%
# Definição dos hyperparâmetros
#Escolha dos melhores hiperparâmetros (max_depth e n_estimators)
gs_cv = GridSearchCV(rf, param_grid, scoring = 'balanced_accuracy', cv = 4, verbose=2, n_jobs = -1).fit(X_data, y)
hyper = gs_cv.best_params_

#%%
# Aplicação de monte carlo pra definir qual a melhor separação dos dados de treinamento e teste

MC_resultados = pd.DataFrame(index = [k for k in range(0,1000)], columns = ['accuracy','precision','recal'])
mode_metrics = pd.DataFrame(index = ['mode'], columns = ['accuracy','precision','recal'])
X_train_MC = []
y_train_MC = []
X_test_MC = []
y_test_MC = []

for a in range(0,1000):
    # Dividir os dados em dados de treinamento e de teste:
    X_train, X_test, y_train, y_test = train_test_split(X_data, y, test_size = 0.25, stratify = y)
    
    # Guarda os dados de treinamento e teste em tabelas
    X_train_MC.append(X_train)
    y_train_MC.append(y_train)
    X_test_MC.append(X_test)
    y_test_MC.append(y_test)
    
    model = RandomForestClassifier(bootstrap = True, max_depth = hyper['max_depth'], min_samples_leaf = 1, min_samples_split = 2, n_estimators = hyper['n_estimators'], random_state = 42)
    y_pred = executar_classificador(model, X_train, y_train, X_test)
                                                 
    # Cálculo das métricas
    MC_resultados.loc[a,'accuracy'] = accuracy_score(y_test, y_pred)
    MC_resultados.loc[a,'precision'] = precision_score(y_test, y_pred, pos_label = 'Classe 1')
    MC_resultados.loc[a,'recal'] = recall_score(y_test, y_pred, pos_label = 'Classe 1')
                                             
# Cálculo da moda das métricas a partir da aplicação de MC
mode_metrics.loc[:,'accuracy'] = MC_resultados[['accuracy']].mode().values[0]
mode_metrics.loc[:,'precision'] = MC_resultados[['precision']].mode().values[0]
mode_metrics.loc[:,'recal'] = MC_resultados[['recal']].mode().values[0]

#%%
# Verificar em qual iteração [0,1000] as métricas estatísticas ficaram mais próximas da moda

k_close, = np.where(MC_resultados.loc[:,'accuracy'].values == mode_metrics.loc[:,'accuracy'].values)

# Cria um dataframe contendo os dados de treinamento e teste correspondente ao valor de k_close
train_dataset = pd.DataFrame(index = [k for k in range(0,114)], columns = dataset.columns)
test_dataset = pd.DataFrame(index = [k for k in range(0,39)], columns = dataset.columns)

train_dataset.iloc[:,1:7] = X_train_MC[k_close[0]]
train_dataset.iloc[:,0] = y_train_MC[k_close[0]]
train_dataset.set_index(X_train_MC[k_close[0]].index, inplace=True)

test_dataset.iloc[:,1:7] = X_test_MC[k_close[0]]
test_dataset.iloc[:,0] = y_test_MC[k_close[0]]
test_dataset.set_index(X_test_MC[k_close[0]].index, inplace=True)

train_dataset.to_csv('G:/Outros computadores/Meu modelo Laptop (1)/Documents/Mestrado/decision_tree/RF_Train.csv')
test_dataset.to_csv('G:/Outros computadores/Meu modelo Laptop (1)/Documents/Mestrado/decision_tree/RF_Test.csv')


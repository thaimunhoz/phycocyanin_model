# -*- coding: utf-8 -*-
"""
Created on Wed Aug 31 15:03:30 2022

@author: thain
"""

# Bibliotecas:
    
import pandas as pd
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.ensemble import RandomForestClassifier
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn import tree
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import train_test_split

# Dados de entrada:
#   - feaures: Relações espectrais -> x
#   - target: Classes -> y

dataset = pd.read_excel('G:/Outros computadores/Meu modelo Laptop (1)/Documents/Mestrado/decision_tree/features_initial.xlsx',header=0, index_col=0)

X = dataset.iloc[:,1:21].values
y = dataset.iloc[:,0].values

X_data = dataset.iloc[:,1:21]

cor = X_data.corr()
new_cor = np.tril(cor)
new_cor[new_cor == 0] = 2 

corr_pd = pd.DataFrame(index = cor.index, columns = cor.columns)
corr_pd.iloc[:,:] = new_cor

# Coeficiente de Pearson:
pearson = np.arange(0.5,1,step=0.05)

#%%
def executar_classificador(classificador, x_train,y_train,x_test):
    arvore = classificador.fit(x_train, y_train)
    y_pred = arvore.predict(x_test)
    return y_pred

def validador(x,y):
    validador = StratifiedShuffleSplit(n_splits=1, test_size = 0.25, random_state=0)
    for treino_id, teste_id in validador.split(x,y):
        x_train, x_test = x[treino_id], x[teste_id]
        y_train, y_test = y[treino_id], y[teste_id]
    return x_train, x_test, y_train, y_test

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
# O algoritmo vai ser todo aplicado para diferentes valores de Pearson, para cada valor definidido, diferentes conjuntos de features
# serão utilizadas para alimentar o modelo (a ideia é ir excluindo features colineares)
pearson_metrics = pd.DataFrame(index = [i for i in pearson], columns = ['accuracy','precision','recal'])
feat_select = []

for i in pearson:
    
    X_data = dataset.iloc[:,1:21]
    end = len(X_data.columns)
    corr_pd = pd.DataFrame(index = cor.index, columns = cor.columns)
    corr_pd.iloc[:,:] = new_cor
    
    # Deleta as features com grau de correlação maior do que o valor de Pearson
    for k in range(0,end):
        if k >= len(X_data.columns):
            break
        res = corr_pd[(abs(corr_pd.iloc[:,k])>= i) & (corr_pd.iloc[:,k] < 1)].iloc[:,k]
        features_delete = res.index.tolist()
        X_data = X_data.drop(features_delete,axis=1)
        corr_pd = corr_pd.drop(features_delete,axis=1)
        corr_pd = corr_pd.drop(features_delete,axis=0)
    
    feat_select.append(X_data.columns)
    
    #Escolha dos melhores hiperparâmetros (max_depth e n_estimators)
    gs_cv = GridSearchCV(rf, param_grid, scoring = 'balanced_accuracy', cv = 4, verbose=2, n_jobs = -1).fit(X_data, y)
    hyper = gs_cv.best_params_
    
    #Aplicação do modelo utilizando Monte Carlo simulation
    
    # Cada tabela criada aqui terá 1000 valores, uma para cada divisão de dados em treinamento e teste. Será escolhida aquela mais próxima da moda
    MC_resultados = pd.DataFrame(index = [k for k in range(0,1000)], columns = ['accuracy','precision','recal'])

    for a in range(0,1000):
        #Divisão dos dados em teste e treinamento
        X_train, X_test, y_train, y_test = train_test_split(X_data, y, test_size = 0.25, stratify = y)
        
        model = RandomForestClassifier(bootstrap = True, max_depth = hyper['max_depth'], min_samples_leaf = 1, min_samples_split = 2, n_estimators = hyper['n_estimators'], random_state = 42)
        y_pred = executar_classificador(model, X_train, y_train, X_test)
        
        # Cálculo das métricas
        MC_resultados.loc[a,'accuracy'] = accuracy_score(y_test, y_pred)
        MC_resultados.loc[a,'precision'] = precision_score(y_test, y_pred, pos_label = 'Classe 1')
        MC_resultados.loc[a,'recal'] = recall_score(y_test, y_pred, pos_label = 'Classe 1')
    
    # Cálculo da média das métricas a partir da aplicação de MC
    pearson_metrics.loc[i,'accuracy'] = MC_resultados[['accuracy']].mean().values[0]
    pearson_metrics.loc[i,'precision'] = MC_resultados[['precision']].mean().values[0]
    pearson_metrics.loc[i,'recal'] = MC_resultados[['recal']].mean().values[0]

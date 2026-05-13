# -*- coding: utf-8 -*-
"""
Created on Tue Aug 30 14:16:15 2022

@author: thain
"""

# Escolha ds features do modelo de classificação 

# Bibliotecas:
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from skfeature.function.similarity_based import fisher_score
import numpy as np
from scipy.sparse import *
from skfeature.utility.construct_W import construct_W
import ppscore as pps

#%%
dataset = pd.read_excel('G:/Outros computadores/Meu modelo Laptop (1)/Documents/Mestrado/decision_tree/features_initial.xlsx',index_col=0)

#%%
# Análise Paiplot:
sns.pairplot(dataset, hue = 'Classes')

#%%
def fisher_score(X, y):
    """
    This function implements the fisher score feature selection, steps are as follows:
    1. Construct the affinity matrix W in fisher score way
    2. For the r-th feature, we define fr = X(:,r), D = diag(W*ones), ones = [1,...,1]', L = D - W
    3. Let fr_hat = fr - (fr'*D*ones)*ones/(ones'*D*ones)
    4. Fisher score for the r-th feature is score = (fr_hat'*D*fr_hat)/(fr_hat'*L*fr_hat)-1
    Input
    -----
    X: {numpy array}, shape (n_samples, n_features)
        input data
    y: {numpy array}, shape (n_samples,)
        input class labels
    Output
    ------
    score: {numpy array}, shape (n_features,)
        fisher score for each feature
    Reference
    ---------
    He, Xiaofei et al. "Laplacian Score for Feature Selection." NIPS 2005.
    Duda, Richard et al. "Pattern classification." John Wiley & Sons, 2012.
    """

    # Construct weight matrix W in a fisherScore way
    kwargs = {"neighbor_mode": "supervised", "fisher_score": True, 'y': y}
    W = construct_W(X, **kwargs)

    # build the diagonal D matrix from affinity matrix W
    D = np.array(W.sum(axis=1))
    L = W
    tmp = np.dot(np.transpose(D), X)
    D = diags(np.transpose(D), [0])
    Xt = np.transpose(X)
    t1 = np.transpose(np.dot(Xt, D.todense()))
    t2 = np.transpose(np.dot(Xt, L.todense()))
    # compute the numerator of Lr
    D_prime = np.sum(np.multiply(t1, X), 0) - np.multiply(tmp, tmp)/D.sum()
    # compute the denominator of Lr
    L_prime = np.sum(np.multiply(t2, X), 0) - np.multiply(tmp, tmp)/D.sum()
    # avoid the denominator of Lr to be 0
    D_prime[D_prime < 1e-12] = 10000
    lap_score = 1 - np.array(np.multiply(L_prime, 1/D_prime))[0, :]

    # compute fisher score from laplacian score, where fisher_score = 1/lap_score - 1
    score = 1.0/lap_score - 1
    return np.transpose(score)


def feature_ranking(score):
    """
    Rank features in descending order according to fisher score, the larger the fisher score, the more important the
    feature is
    """
    idx = np.argsort(score, 0)
    return idx[::-1]
#%%
# Cálculo do Fisher Score:
x = dataset.iloc[:,1:21].to_numpy()
y = dataset.iloc[:,0].to_numpy()

ranks = fisher_score(x,y)

feat_importances = pd.Series(feature_ranking(ranks), dataset.columns[1:len(dataset.columns)])
feat_importances.plot(kind='barh', color = 'teal')
plt.show()

#%%
# PPS Score
res_pps = pps.predictors(dataset, 'Classes')
plt.figure(figsize=(22,7))
sns.barplot(data=res_pps, x="x", y="ppscore")

plt.ylabel('PPS',weight='bold', fontsize=28)
plt.xlabel('Bio-optical models',weight='bold', fontsize=28)
plt.xticks( fontsize=28, rotation = 45)
plt.yticks( fontsize=28)
#%%
matrix_df = pps.matrix(dataset)[['x', 'y', 'ppscore']].pivot(columns='x', index='y', values='ppscore')
plt.figure(figsize=(20,20))
sns.heatmap(matrix_df, vmin=0, vmax=1, cmap="Blues", linewidths=0.5, annot=True)

#%%
# Matriz de correlação:
cor = dataset.corr()
plt.figure(figsize=(20,20))
sns.heatmap(cor,annot=True)
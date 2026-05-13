# -*- coding: utf-8 -*-
"""
Created on Tue Mar  1 20:34:00 2022

@author: thain
"""
# Lê o arquivo .txt com a FRS do OLCI e interpola para cada nm

import pandas as pd
import scipy.interpolate
import numpy as np
import matplotlib.pyplot as plt

#%%
# Leitura das bandas separadamente
bandas = []

for i in range(1,22):
    data = pd.read_excel('G:/Outros computadores/Meu modelo Laptop (1)/Documents/Mestrado/OLCI_band_simulation/S3B_OLCI_SRF.xlsx',index_col=0,sheet_name="BAND Oa"+str(i))
    bandas.append(data)
    
#%%
# Cria uma lista com os comprimentos de onda a serem interpolados
# Cada coluna corresponde ao intervalo espectral da respectiva banda
waves = []

for k in range(0,21):
    aux = bandas[k] # Acessa a banda k
    waves.append(np.arange(int(aux.index.values[0])+1,aux.index.values[-1],step=1))

#%%
# Interpolação
res_final = pd.DataFrame(index = np.arange(300,1100,step=1))

for k in range(0,21):
    
    aux = bandas[k]
    x = aux.index.values
    y = aux.iloc[:,0].values
    y_interp = scipy.interpolate.interp1d(x, y)
    new_band = y_interp(waves[k])
    
    aux_pd = pd.DataFrame(index = waves[k], columns =[k])
    aux_pd.loc[:,k] = new_band
    
    res_final = res_final.join(aux_pd)
    del aux_pd

res_final = res_final.fillna(0)

#%%
# Salvar dicionário em csv
# determining the name of the file
file_name = 'G:/Outros computadores/Meu modelo Laptop (1)/Documents/Mestrado/OLCI_band_simulation/S3B_FRS_1nm.xlsx'
  
# saving the excel
res_final.to_excel(file_name)
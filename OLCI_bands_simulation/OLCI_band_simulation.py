# -*- coding: utf-8 -*-
"""
Created on Wed Mar  2 09:49:11 2022

@author: thain
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

oli_fre = pd.read_excel('G:/Outros computadores/Meu modelo Laptop (1)/Documents/Mestrado/OLCI_band_simulation/S3B_FRS_1nm_clip.xlsx', header=0, index_col=0)

lista_bandas = []

#%%
# cria lista de bandas para OLCI
for a in range(1, 22):
    banda = "B" + str(a)
    lista_bandas.append(banda)

#%%
#criar variável fator de correção (FRE/SOMA SRF)
for a in lista_bandas:
    oli_fre[a] *= (1/oli_fre[a].sum())

#%%
#importar os dados de campo
diretorio = 'G:/Outros computadores/Meu modelo Laptop (1)/Documents/Mestrado/OLCI_band_simulation/Rrs_in_situ.xlsx'

field_spec = pd.read_excel(diretorio,header=0, index_col=0, sheet_name = 'Sheet3')

fc = oli_fre
print(fc)
print(field_spec)

#%%
#cria dataframe vazio para preenche com dados
df = pd.DataFrame(index=[400,412.5,442.5,490,510,560,620,665,673.5,681.25,708.75,753.75,761.25,764.375,767.5,778.75,865,885,900,940,1020])

#lista com nomes das colunas
list_of_column = list(field_spec)
print(list_of_column)

#%%
for a in list_of_column:

    simulated_bands = []
    list_of_bands = fc.columns.values.tolist()

    for b in list_of_bands:

        spec = field_spec[a].to_numpy()
        fc_esp = fc[b].to_numpy()
        banda_sim = np.multiply(spec, fc_esp)
        banda_simu = sum(banda_sim)
        simulated_bands.append(banda_simu)

    df[a] = simulated_bands

#%%
plt.figure(figsize=(10,8))
for a in list_of_column:
    plt.plot(df.index, df[a], c=np.random.rand(3, ))

plt.xlabel(r"Wavelength [nm]", fontsize=30)
plt.ylabel("$Rrs$ $[Sr^{-1}]$", fontsize=30)
plt.xticks(fontsize=26)
plt.yticks(fontsize=26)
plt.xlim(400, 900)
plt.ylim(0, 0.12)
plt.grid()
plt.show()

plt.figure(figsize=(10,8))

for a in list_of_column:
    plt.plot(field_spec.index, field_spec[a])

plt.xlabel(r"Wavelength [nm]", fontsize=30)
plt.ylabel("$Rrs$ $[Sr^{-1}]$", fontsize=30)
plt.rcParams.update({'font.size': 26})
plt.xlim(400, 900)
plt.ylim(0, 0.12)
plt.xticks(fontsize=26)
plt.yticks(fontsize=26)
plt.grid()
plt.show()

#%%
# determining the name of the file
file_name = 'G:/Outros computadores/Meu modelo Laptop (1)/Documents/Mestrado/OLCI_band_simulation/S3B_simulated_agosto2022.xlsx'
  
# saving the excel
df.to_excel(file_name)
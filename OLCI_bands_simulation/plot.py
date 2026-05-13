# -*- coding: utf-8 -*-
"""
Created on Wed Jan  4 07:38:53 2023

@author: thain
"""

# bibliotecas:
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import math

#Leitura dos arquivos:
original = pd.read_excel(r'G:\Outros computadores\Meu modelo Laptop (1)\Documents\Mestrado\OLCI_band_simulation\Rrs_simulated_all.xlsx', sheet_name = 'original', index_col=0)
prisma = pd.read_excel(r'G:\Outros computadores\Meu modelo Laptop (1)\Documents\Mestrado\OLCI_band_simulation\Rrs_simulated_all.xlsx', sheet_name = 'PRISMA', index_col=0)
olci = pd.read_excel(r'G:\Outros computadores\Meu modelo Laptop (1)\Documents\Mestrado\OLCI_band_simulation\Rrs_simulated_all.xlsx', sheet_name = 'OLCI', index_col=0)

#%%
fig2, (ax, ax2, ax3) = plt.subplots(figsize=(30,10),ncols=3, sharey=True)

for a in original.index:
    ax.plot(original.columns, original.loc[a,:], c=np.random.rand(3, ), linewidth = 2, marker = 'o', markersize = 1)

ax.set_ylabel("Rrs ($sr^{-1}$)", weight = 'bold', fontsize=30)
ax.tick_params(axis='both', labelsize=28)
ax.set_xlim(400, 900)
ax.set_ylim(0, 0.12)
ax.set_title('Original',fontsize=35, weight = 'bold')
ax.grid()

for a in olci.index:
    ax2.plot(olci.columns, olci.loc[a,:], c=np.random.rand(3, ), linewidth = 2, marker = 'o', markersize = 1)

ax2.set_xlabel("Wavelength (nm)", weight = 'bold', fontsize=30)
ax2.tick_params(axis='both', labelsize=28)
ax2.set_xlim(400, 900)
ax2.set_ylim(0, 0.12)
ax2.set_title('OLCI resampled',fontsize=35, weight = 'bold')
ax2.grid()

for a in prisma.index:
    ax3.plot(prisma.columns, prisma.loc[a,:], c=np.random.rand(3, ), linewidth = 2, marker = 'o', markersize = 1)

#ax3.set_ylabel("$Rrs$ $[Sr^{-1}]$", weight = 'bold', fontsize=30)
ax3.tick_params(axis='both', labelsize=28)
ax3.set_xlim(400, 900)
ax3.set_ylim(0, 0.12)
ax3.set_title('PRISMA resampled',fontsize=35, weight = 'bold')
ax3.grid()

ax.set_box_aspect(1)
ax2.set_box_aspect(1)
ax3.set_box_aspect(1)
plt.show()
#%%
fig2, ax = plt.subplots(figsize=(15,15))

for a in prisma.index:
    ax.plot(prisma.columns, prisma.loc[a,:], color= 'midnightblue', linewidth = 2, marker = 'o', markersize = 1)
ax.set_title('PRISMA resampled',fontsize=35, weight = 'bold')
ax.set_ylabel("Rrs ($sr^{-1}$)", fontsize=30)
ax.set_xlabel("Wavelength (nm)", fontsize=30)
ax.tick_params(axis='both', labelsize=28)
ax.set_xlim(400, 900)
ax.set_ylim(0, 0.12)
ax.grid()
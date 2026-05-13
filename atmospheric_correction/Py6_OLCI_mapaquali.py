# -*- coding: utf-8 -*-
"""
Created on Fri Feb 24 19:52:00 2023

@author: thain
"""
# Py6s OLCI

from Py6S import *
import pandas as pd
import numpy as np
import csv
import xarray as xr

def find_nearest(a, a0):
    "Element in nd array `a` closest to the scalar value `a0`"
    idx = a.flat[np.abs(a - a0).argmin()]
    index = np.where(a == idx)
    return index

def extract_geom(Lat,Lon, tie_geo_coordinates_path, tie_geometries_path):
    # Arquivo contendo as informações da geometria de aquisição
    nc_file = xr.open_dataset(tie_geometries_path)
    
    # Arquivo contendo as informações de latitude e longitude
    nc_coordinates = xr.open_dataset(tie_geo_coordinates_path)
    
    olci_lat = nc_coordinates['latitude'] #indica a variação na vertical -> valor da linha
    olci_lon = nc_coordinates['longitude'] #indica a variação na horizontal -> valor da coluna

    # Encontra o indíce (linha e coluna) correspondente a latitude e longitude do ponto escolhido
    index_lat = find_nearest(olci_lat.values, Lat)[0]
    index_long = find_nearest(olci_lon.values, Lon)[1]

    OAA = nc_file['OAA'][index_lat,index_long].values # Observation (Viewing) Azimuth Angle
    OZA = nc_file['OZA'][index_lat,index_long].values # Observation (Viewing) Zenith Angle
    SAA = nc_file['SAA'][index_lat,index_long].values # Sun Azimuth Angle
    SZA = nc_file['SZA'][index_lat,index_long].values # Sun Zenith Angle

    return OZA[0][0], SAA[0][0], SZA[0][0], OAA[0][0]

#%%
# Variáveis de entrada

# extrair informação de ângulos de iluminação e visada:--------------------------------------
tie_geometries_path = r'G:\Outros computadores\Meu modelo Laptop (1)\Documents\Mestrado\OLCI_images\dissertacao\OL_1_FR\OL1_EFR_03-10-2021\S3B_OL_1_EFR____20211003T125121_20211003T125421_20211004T164329_0179_057_323_3240_LN1_O_NT_002.SEN3\tie_geometries.nc'
tie_geo_coordinates_path = r'G:\Outros computadores\Meu modelo Laptop (1)\Documents\Mestrado\OLCI_images\dissertacao\OL_1_FR\OL1_EFR_03-10-2021\S3B_OL_1_EFR____20211003T125121_20211003T125421_20211004T164329_0179_057_323_3240_LN1_O_NT_002.SEN3\tie_geo_coordinates.nc'

# Coordenadas de um ponto qualquer dentro da área de interesse
Lat = -21.39
Lon = -49.584808
# Angulo zenital do sensor (OZA), Angulo solar zenital (SZA), Angulo solar azimutal (SAA)
view_Zn, solar_Az, solar_Zn, view_Az = extract_geom(Lat, Lon, tie_geo_coordinates_path, tie_geometries_path)

aod550 = 0.0751980
alt_alvo = 0.38607053 #km

# Informação de dia e mes
date = tie_geometries_path.split("EFR____",1)[1][:8]
if date[6:-1] == '0':
    day_ = int(date[-1])
else:
    day_ = int(date[6:])

month_ = int(date[4:-2])

#%%
# Função que permite o acesso ao modelo 6S
s = SixS()

#%%
# Perfil atmosférico:
# Considera as características associadas a este perfil (vapor d'água e ozonio) e incorpora no modelo
s.atmos_profile = AtmosProfile.PredefinedType(AtmosProfile.Tropical)

#Aerossol:
s.aot550 = aod550
#Modelo de aerossol a ser utilizado (define a distribuição, tamanho das partículas, caracteristicas físicas, etc)
s.aero_profile = AeroProfile.PredefinedType(AeroProfile.Continental)

# Ground Reflectance-------------------------------------------------------------------------------------------:
s.ground_reflectance = GroundReflectance.HomogeneousLambertian(np.array([[0.419, 0.427, 0.434, 0.442, 0.449, 0.456, 0.464, 0.471, 0.478,0.485, 0.493, 0.5  , 0.508, 0.515, 0.523, 0.531, 0.538, 0.546,0.555, 0.563, 0.571, 0.579, 0.588, 0.596, 0.605, 0.614, 0.623,0.632, 0.641, 0.651, 0.66 , 0.67 , 0.679, 0.689, 0.699, 0.709,0.719, 0.729, 0.739, 0.75 , 0.76 , 0.771, 0.781, 0.791, 0.802,0.813, 0.823, 0.834, 0.844, 0.855, 0.866, 0.877], [0.01445915, 0.01422249, 0.01406214, 0.01449518, 0.01592469,0.01761156, 0.01887088, 0.01983343, 0.02057033, 0.02136334, 0.02239862, 0.02424129, 0.02697532, 0.03056817, 0.03507325,0.04024491, 0.04571142, 0.05035407, 0.05309473, 0.0534503 ,0.05134707, 0.04744315, 0.04276923, 0.03773851, 0.03321408, 0.03015397, 0.02826281, 0.02778316, 0.02844564, 0.02861082,0.02545578, 0.02104192, 0.02031077, 0.0262125 , 0.03404532,0.03589206, 0.03120186, 0.023576  , 0.01819808, 0.01653794, 0.01646553, 0.01618563, 0.01658291, 0.01753715, 0.01833317,0.01814674, 0.01594022, 0.01273109, 0.01097039, 0.01016107,0.00947185, 0.00875745]]))

# Geometries of view and illumination--------------------------------------------------------------------------:
s.geometry = Geometry.User()
s.geometry.day = day_
s.geometry.month = month_
s.geometry.solar_z = float(solar_Zn)
s.geometry.solar_a = float(solar_Az)
s.geometry.view_z = float(view_Zn)
s.geometry.view_a = float(view_Az)

# Altitudes---------------------------------------------------------------------------------------------------:
s.altitudes = Altitudes()
s.altitudes.set_sensor_satellite_level()  # Set the sensor altitude to be satellite level.
s.altitudes.set_target_custom_altitude(alt_alvo)  # The altitude of the target (in km).

#%%
# Função de interpolação 
def _interpolate_(dataframe_):
    import scipy.interpolate
    a = np.arange(300,1099,2.5)
    new_srf = [] # Recebe os novos valores de SRF para cada banda
    for k in range(0,len(dataframe_)):
        y = dataframe_.iloc[k,:]
        x = dataframe_.columns
        y_interp = scipy.interpolate.interp1d(x, y, fill_value="extrapolate")
        new_srf.append(y_interp(a)) 
    arr = np.asarray(new_srf)
    new_bands = pd.DataFrame(arr, index = dataframe_.index, columns = a)
    return(new_bands)

#%%
# Função de resposta espectral do OLCI
# frs -> linhas: comprimento de onda; colunas: bandas
frs = pd.read_excel(r'G:\Outros computadores\Meu modelo Laptop (1)\Documents\Mestrado\OLCI_band_simulation\S3A_FRS_1nm.xlsx',index_col=0)
frs = frs.transpose()
frs_nova = _interpolate_(frs)
frs_nova_transposed = frs_nova.transpose()
frs = frs.transpose()

#%%
# Rodar o 6S para cada banda espectral    
dicionario = {}
waves_6s = []
waves_max_int = []

for a in range(0,frs_nova_transposed.shape[1]):
    
    max_value_index = frs_nova_transposed[frs_nova_transposed.iloc[:,a]==frs_nova_transposed.iloc[:,a].max()].index.values[0]
    waves_max_int.append(max_value_index)
    
    wv_value = frs_nova_transposed.columns.values[a]
    
    # Comparação dos comprimentos de onda (não usa pra nada)
    max_value_temp = frs[frs.iloc[:,a]==frs.iloc[:,a].max()].index.values[0]
    waves_6s.append(max_value_temp)
     
    srf_values = list(frs_nova_transposed.loc[300:1097.5,wv_value])
    
    s.wavelength = Wavelength((300/1000),(1097.5/1000),srf_values)
    
    s.run()
    
    print(s.wavelength)
    
    # Alguns parâmetros importantes não estão contidos no output do modelo. Podemos recuperar esses valores:
    #s.outputs.values['transmittance_total_scattering'] = s.outputs.transmittance_total_scattering.total
    s.outputs.values['spherical_albedo'] = s.outputs.spherical_albedo.total
    s.outputs.values['co_transmittance_total'] = s.outputs.transmittance_co.total
    s.outputs.values['co2_transmittance_total'] = s.outputs.transmittance_co2.total
    s.outputs.values['oxyg_transmittance_total'] = s.outputs.transmittance_oxygen.total
    s.outputs.values['no2_transmittance_total'] = s.outputs.transmittance_no2.total
    s.outputs.values['ch4_transmittance_total'] = s.outputs.transmittance_ch4.total
    s.outputs.values['ozone_transmittance_total'] = s.outputs.transmittance_ozone.total
    s.outputs.values['water_transmittance_total'] = s.outputs.transmittance_water.total
    s.outputs.values['total_scattering_transmittance_upward'] = s.outputs.transmittance_total_scattering.upward
    s.outputs.values['total_scattering_transmittance_downward'] = s.outputs.transmittance_total_scattering.downward
    
    dicionario[str(int(max_value_temp))] = s.outputs.values #Guarda dentro de um dicionário, para cada banda, os dados de saída do 6S
 
#%%
# Salva dicionário em json
import json
a_file = open(r"G:\Outros computadores\Meu modelo Laptop (1)\Documents\Mestrado\mapaquali\atmospheric_correction\6S_parameters_OLCI_03102021.json", "w")
json.dump(dicionario, a_file)

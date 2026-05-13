# -*- coding: utf-8 -*-
"""
Created on Wed Oct  5 09:27:13 2022

@author: thain
"""

# Library:
import numpy as np
from osgeo import gdal
import pandas as pd
import json
from osgeo import osr

# Funções
def GetGeoInfo(FileName):
    SourceDS = gdal.Open(FileName, gdal.GA_ReadOnly)
    NDV = SourceDS.GetRasterBand(1).GetNoDataValue()
    xsize = SourceDS.RasterXSize
    ysize = SourceDS.RasterYSize
    GeoT = SourceDS.GetGeoTransform()
    Projection = osr.SpatialReference()
    Projection.ImportFromWkt(SourceDS.GetProjectionRef())
    DataType = SourceDS.GetRasterBand(1).DataType
    DataType = gdal.GetDataTypeName(DataType)
    return NDV, xsize, ysize, GeoT, Projection, DataType

#%%
# Excel file containing the central wavelenght, fwhm, name of each band for the specific image
# IMPORTANT -> The number of bands must be equal to the spectral response function
bands_prisma = pd.read_excel(
    r'G:\Outros computadores\Meu modelo Laptop (1)\Documents\Mestrado\mapaquali\atmospheric_correction\olci_bands.xlsx', header=0, index_col=0)
bands_prisma_acolite = bands_prisma.iloc[:, 0].values

# TOA Reflectance -> each band must be saved in a unique file EM REFLECTANCIA
path_to_toa_reflectance = r'G:\Outros computadores\Meu modelo Laptop (1)\Documents\Mestrado\OLCI_images\dissertacao\OL_1_FR\OL1_EFR_03-10-2021\bands_reflectancia_TOA\_band'

# Read the JSON file
with open(r'G:\Outros computadores\Meu modelo Laptop (1)\Documents\Mestrado\mapaquali\atmospheric_correction\6S_parameters_OLCI_03102021.json') as f:
    data = f.read()

dicionario = json.loads(data)

dic_aux = dicionario

a = 0
for k in list(dic_aux.keys()):
    dicionario[str(bands_prisma_acolite[a])] = dicionario.pop(str(k))
    a = a + 1

#%%
# Apply the radiative transfer equation in each RTOA image considering the parameters from the 6S
NDV, xsize, ysize, GeoT, Projection, DataType = GetGeoInfo(path_to_toa_reflectance + str(1) + ".tif")

ac_corrected_bands = np.zeros((ysize,xsize,21)) #ysize (lin), xsize (col)

for a in bands_prisma.index:

    string_band = path_to_toa_reflectance + str(a) + ".tif"
    band_prisma = gdal.Open(string_band, gdal.GA_ReadOnly)
    
    NDV, xsize, ysize, GeoT, Projection, DataType = GetGeoInfo(string_band)
    driver = gdal.GetDriverByName('GTiff')

    array_prisma = band_prisma.GetRasterBand(1).ReadAsArray()

    # Atmospheric modeling:
    atmospheric_modeling_py6S_Band = dicionario[str(bands_prisma_acolite[a-1])]

    # Atmospheric Correction -> Equation Vermote et al. (2016):
    tg_OG_co = float(atmospheric_modeling_py6S_Band['co_transmittance_total'])
    tg_OG_c02 = float(
        atmospheric_modeling_py6S_Band['co2_transmittance_total'])
    tg_OG_o2 = float(
        atmospheric_modeling_py6S_Band['oxyg_transmittance_total'])
    tg_OG_no2 = float(
        atmospheric_modeling_py6S_Band['no2_transmittance_total'])
    tg_OG_ch4 = float(
        atmospheric_modeling_py6S_Band['ch4_transmittance_total'])

    # Total transmission of Other Gases -> Tg_OG:
    Tg_OG = float(tg_OG_co * tg_OG_c02 * tg_OG_o2 * tg_OG_no2 * tg_OG_ch4)

    # Total transmission of the Ozone -> Tg_O3:
    Tg_O3 = float(atmospheric_modeling_py6S_Band['ozone_transmittance_total'])

    # Total transmission of the Water Vapor -> Tg_H2O:
    Tg_H20 = float(atmospheric_modeling_py6S_Band['water_transmittance_total'])

    # Total transmittance upward (Rayleigh + Aerosol) -> T_upward:
    T_upward = float(
        atmospheric_modeling_py6S_Band['total_scattering_transmittance_upward'])

    # Total transmittance downward (Rayleigh + Aerosol) -> T_downward:
    T_downward = float(
        atmospheric_modeling_py6S_Band['total_scattering_transmittance_downward'])

    # Total transmission of the atmosphere -> T_atm:
    T_atm = float(T_upward * T_downward)

    # Atmosphere intrinsic reflectance -> p_atm:
    p_atm = float(
        atmospheric_modeling_py6S_Band['atmospheric_intrinsic_reflectance'])

    # Atmosphere spherical albedo -> s_atm:
    s_atm = float(atmospheric_modeling_py6S_Band['spherical_albedo'])

    # Equation (Ref: Vermonte et al., 1997)
    f1 = Tg_OG * Tg_O3 * Tg_H20 * T_atm
    f2 = p_atm / (Tg_H20 * T_atm)
    parte_1 = np.divide(array_prisma, f1)
    parte_2 = np.subtract(parte_1, f2)
    parte_3 = np.multiply(parte_2, s_atm)
    parte_4 = np.add(parte_3, 1)
    p_s = parte_2 / parte_4

    rrs = np.divide(p_s,np.pi)
    
    ac_corrected_bands[:,:,a-1] = rrs
    
    print(a)

print('FIM')

#%%
Name = r'G:\Outros computadores\Meu modelo Laptop (1)\Documents\Mestrado\mapaquali\atmospheric_correction\olci_03102021_6S_rrs_teste.tif'
if DataType == 'Float32':
    DataType = gdal.GDT_Float32
        
ac_corrected_bands[np.isnan(ac_corrected_bands)] = NDV
DataSet = driver.Create(Name, ac_corrected_bands.shape[1], ac_corrected_bands.shape[0], ac_corrected_bands.shape[2], DataType)
DataSet.SetGeoTransform(GeoT)
DataSet.SetProjection( Projection.ExportToWkt() )
band = ac_corrected_bands.shape[2]
for i in range(band):
    DataSet.GetRasterBand(i+1).WriteArray(ac_corrected_bands[:,:,i])
    #DataSet.GetRasterBand(i+1).SetNoDataValue(NDV)
DataSet.FlushCache()# -*- coding: utf-8 -*-


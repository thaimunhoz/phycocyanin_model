# -*- coding: utf-8 -*-
"""
Created on Fri Feb 24 20:23:01 2023

@author: thain
"""

# Aplicação do modelo hybrido em imagens OLCI

# Bibliotecas:
    
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import numpy as np
from osgeo import gdal
from osgeo import osr
import math
import scipy.sparse

# Function to read the original file's projection:
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

# Function to save the final raster as a tiff file
def CreateGeoTiff(Name, Array, driver, NDV, 
                  xsize, ysize, GeoT, Projection, DataType):
    if DataType == 'Float32':
        DataType = gdal.GDT_Float32
    NewFileName = Name+'.tif'
    # Set nans to the original No Data Value
    #Array[np.isnan(Array)] = NDV
    # Set up the dataset
    DataSet = driver.Create( NewFileName, xsize, ysize, 1, DataType )
            # the '1' is for band 1.
    DataSet.SetGeoTransform(GeoT)
    DataSet.SetProjection( Projection.ExportToWkt() )
    # Write the array
    DataSet.GetRasterBand(1).WriteArray( Array )
    #DataSet.GetRasterBand(1).SetNoDataValue(NaN)
    return NewFileName

def executar_classificador(classificador, x_train,y_train,x_test):
    arvore = classificador.fit(x_train, y_train)
    y_pred = arvore.predict(x_test)
    return y_pred

def median_sym_accuracy(y_true, predictions):
    index_neg = []
    for bb in range(0,len(y_true)):
        if predictions[bb] < 0:
            index_neg.append(bb)
    new_y_true = np.delete(y_true, index_neg)
    new_prediction = np.delete(predictions, index_neg)
    
    log_q = abs(np.log(np.divide(new_prediction,new_y_true)))
    #log_q[~np.isnan(log_q).any(axis=1)]
    e = 100 * (math.exp(np.median(log_q)) - 1)
    return e

def bias_(y_true,predictions):
    index_neg = []
    for bb in range(0,len(y_true)):
        if predictions[bb] < 0:
            index_neg.append(bb)
    new_y_true = np.delete(y_true, index_neg)
    new_prediction = np.delete(predictions, index_neg)
    
    log_q = np.log(np.divide(new_prediction,new_y_true))
    bias_p = 100 * np.sign(np.median(log_q)) * (math.exp(abs(np.median(log_q)))-1)
    return bias_p

def mae_log(y_true, predictions):
    index_neg = []
    for bb in range(0,len(y_true)):
        if predictions[bb] < 0:
            index_neg.append(bb)
    new_y_true = np.delete(y_true, index_neg)
    new_prediction = np.delete(predictions, index_neg)
    
    sub_log = abs(np.subtract(np.log(new_prediction),np.log(new_y_true)))
    mae_l = math.exp(np.mean(sub_log))
    return mae_l

def percentage_error(actual, predicted):
    res = np.empty(actual.shape)
    for j in range(actual.shape[0]):
        if actual[j] != 0:
            res[j] = (actual[j] - predicted[j]) / actual[j]
        else:
            res[j] = predicted[j] / np.mean(actual)
    return res

def mean_absolute_percentage_error(y_true, y_pred): 
    return np.mean(np.abs(percentage_error(np.asarray(y_true), np.asarray(y_pred)))) * 100

def mean_filter(arr, k):
    p = len(arr)
    diag_offset = np.linspace(-(k//2), k//2, k, dtype=int)
    eL = scipy.sparse.diags(np.ones((k, p)), offsets=diag_offset, shape=(p, p))
    nrmlize = eL @ np.ones_like(arr)
    return (eL @ arr) / nrmlize

#%%
string_olci = r'G:\Outros computadores\Meu modelo Laptop (1)\Documents\Mestrado\OLCI_images\dissertacao\OL_1_FR\OL1_EFR_03-10-2021\olci_03102021_6S_rrs_teste.tif'

def hybrid_model(string_olci):
    # input data:
        #   - feaures: spectral features -> x
        #   - target: Classes -> y

    # Dados de treinamento para o random forest:
    dataset_train = pd.read_excel('G:/Outros computadores/Meu modelo Laptop (1)/Documents/Mestrado/decision_tree/RF_Train.xlsx',header=0, index_col=0)

    X_train = dataset_train.iloc[:,1:7].values
    y_train = dataset_train.iloc[:,0].values

    # Dados de validação:
    # acessa o endereço da imagem
    image_olci = gdal.Open(string_olci, gdal.GA_ReadOnly)

#Acessa informações da projeção da imagem
    NDV, xsize, ysize, GeoT, Projection, DataType = GetGeoInfo(string_olci)

# Set up the GTiff driver
    driver = gdal.GetDriverByName('GTiff')

# Seleção das bandas da imagem a serem aplicadas no modelo:
    banda_708 = image_olci.GetRasterBand(11).ReadAsArray().astype(float)
    banda_620 = image_olci.GetRasterBand(7).ReadAsArray().astype(float)
    banda_665 = image_olci.GetRasterBand(8).ReadAsArray().astype(float)
    banda_510 = image_olci.GetRasterBand(5).ReadAsArray().astype(float)
    banda_442 = image_olci.GetRasterBand(3).ReadAsArray().astype(float)
    banda_560 = image_olci.GetRasterBand(6).ReadAsArray().astype(float)
    banda_753 = image_olci.GetRasterBand(12).ReadAsArray().astype(float)
    banda_681 = image_olci.GetRasterBand(10).ReadAsArray().astype(float)

# Get the No Data Value
    NDV = image_olci.GetRasterBand(1).GetNoDataValue()
#NDV= 999
# Convert No Data Points to nans
    banda_708[banda_708 == NDV] = np.nan
    banda_620[banda_620 == NDV] = np.nan
    banda_665[banda_665 == NDV] = np.nan
    banda_510[banda_510 == NDV] = np.nan
    banda_442[banda_442 == NDV] = np.nan
    banda_560[banda_560 == NDV] = np.nan
    banda_753[banda_753 == NDV] = np.nan
    banda_681[banda_681 == NDV] = np.nan

#Cálculo dos índices espectrais -> cada índice calculado vai entrar no random forest como se fosse uma banda
#  Lembre-se: cada índice é uma imagem

    SIM05 =  banda_708 / banda_620
    SY00 =  banda_665 / banda_620
    BE16 = banda_510 - (banda_665 + (banda_442 - banda_665))
    NI_5 = (banda_560 - banda_620) / (banda_560 + banda_620)
    LH_5 = banda_708 - (banda_753 - ((banda_681 - banda_753) * ((753.75 -708.75)/(753.75 - 681.25))))
    LH_4 = banda_665 - (banda_681 - ((banda_620 - banda_681) * ((681.25 -665)/(681.25 - 620))))

# Modelo Random Forest
    model = RandomForestClassifier(bootstrap = True, max_depth = 10, min_samples_leaf = 1, min_samples_split = 2, n_estimators = 300, random_state = 42)

# Transforma a imagem (matrix) em um vetor 1D
    SIM05_v = SIM05.flatten().reshape(-1,1)
    SY00_v = SY00.flatten().reshape(-1,1)
    BE16_v = BE16.flatten().reshape(-1,1)
    NI_5_v = NI_5.flatten().reshape(-1,1)
    LH_5_v = LH_5.flatten().reshape(-1,1)
    LH_4_v = LH_4.flatten().reshape(-1,1)

# Cria uma tabela
    y_test_sat = pd.DataFrame(index = [i for i in range(0,len(SIM05_v))], columns = ['SIM05','SY00','BE16','NI5','LH5','LH4'])
    y_test_sat.loc[:,'SIM05'] = SIM05_v
    y_test_sat.loc[:,'SY00'] = SY00_v
    y_test_sat.loc[:,'BE16'] = BE16_v
    y_test_sat.loc[:,'NI5'] = NI_5_v
    y_test_sat.loc[:,'LH5'] = LH_5_v
    y_test_sat.loc[:,'LH4'] = LH_4_v

#Deletar os valores NaN da tabela -> aplicar o random forest nesses valores -> substituir eles nas posições corretas
# y_test_sat -> contém os NaN
# y_test_nan -> NÃO contém os NaN

    y_test_nan = y_test_sat.dropna()
    y_test = y_test_nan.to_numpy()

# aplica o classificador
    y_pred_sat = executar_classificador(model, X_train, y_train, y_test)

# Resultado do modelo (classes) e os respectivos índices corretos de cada pixel
    final = pd.DataFrame(y_pred_sat, index = y_test_nan.index.values, columns = ['classes'])

# Tabela com todos os índices (incluíndo os NaN) -> o resultado vai ser alocado nas respectivas posições
    res = pd.DataFrame(index = y_test_sat.index.values, columns = ['classes'])
    res.iloc[final.index, 0] = final.iloc[:,0].to_numpy()
    res = res.to_numpy()

    imagem_final= res.reshape(banda_708.shape[0],banda_708.shape[1]) #imagem com as classes

# 3 - Após a classificação dos pontos, um algoritmo bio-óptico adequado será aplicado

# Dados de validação (valores de X -> índice espectral)
# Para classe 1 (low PC concentration) -> OGA19 model

#X_1 = pd.DataFrame(index = rrs_simulated.index, columns = ['OGA19'])
    f1= 0.2215
    f2 = 1.1491
    X1_OGA = ((banda_708/banda_620) - ((banda_708/banda_665)*f1)) / (1 - (f1*f2))

# Para classe 2 (high PC concentration) -> LIU17 model
#X_2 = pd.DataFrame(index = rrs_simulated.index, columns = ['LIU17'])
    X2_LIU17 = ((1/banda_620) - (0.4/banda_560) - (0.6/banda_708)) * banda_753

# Dados de treinamento dos modelos
# Classe 1:
    oga_dataset = pd.read_excel(r'G:\Outros computadores\Meu modelo Laptop (1)\Documents\Mestrado\bio_optical_algorithms\classe_1\model5_OGA19\Train_oga.xlsx',header=0, index_col=0)
    X1_train_model = oga_dataset.loc[:,'OGA19']
    y1_train_model = oga_dataset.loc[:,'PC']

# Classe 2:
    liu_dataset = pd.read_excel(r'G:\Outros computadores\Meu modelo Laptop (1)\Documents\Mestrado\bio_optical_algorithms\classe_2\model4_LIU17\Train_liu.xlsx',header=0, index_col=0)
    X2_train_model = liu_dataset.loc[:,'LIU17']
    y2_train_model = liu_dataset.loc[:,'PC']

# Definimos aqui os coeficientes do cálculo da concentração para as duas classes
    m1, b1 = np.polyfit(X1_train_model.values.astype('float64'), y1_train_model.values.astype('float64'), 1)
    m2, b2 = np.polyfit(X2_train_model.values.astype('float64'), y2_train_model.values.astype('float64'), 1)

# Usamos agora uma chave para definir qual o algoritmo a ser aplicado no ponto
    PC_con = pd.DataFrame(index = range(0,imagem_final.shape[0]), columns = range(0,imagem_final.shape[1]))

    for k in range(0,imagem_final.shape[0]): #percorre as linhas
        for b in range(0,imagem_final.shape[1]): #percorre as colunas
            if imagem_final[k,b] == 1: #Significa que o pixel em questão foi identificado com baixa concentração de PC
                PC_con.iloc[k,b] = m1 * X1_OGA[k,b]  + b1 # Aplicação do modelo 1
            elif imagem_final[k,b] == 2:
                PC_con.iloc[k,b] = m2 * X2_LIU17[k,b] + b2 # Aplicação do modelo 2
            else:
                PC_con.iloc[k,b] = np.nan

#PC_con[pd.isna(PC_con)] = 999
        
    PC_con = PC_con.to_numpy()
    PC_con = np.array(PC_con, dtype=float)
    PC_smooth =  mean_filter(PC_con,3)

    NewFileName_pc = CreateGeoTiff(r'G:\Outros computadores\Meu modelo Laptop (1)\Documents\Mestrado\OLCI_images\dissertacao\OL_1_FR\OL1_EFR_03-10-2021\6S_teste_rrs_pc', PC_con, driver, NDV, 

# Salvar a imagem de classicação
    NewFileName_pc = CreateGeoTiff(r'G:\Outros computadores\Meu modelo Laptop (1)\Documents\Mestrado\OLCI_images\dissertacao\OL_1_FR\OL1_EFR_03-10-2021\6S_teste_rrs_classes',imagem_final, driver, NDV, xsize, ysize, GeoT, Projection, DataType)


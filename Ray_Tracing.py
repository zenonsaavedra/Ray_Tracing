#==============================================================================
#Titulo: Ray_Tracing
#Autor: Zenon Saavedra 
#==============================================================================
"""
En este se determina el camino de propagacion seguido por una O.E

Para la deterinacion del camino se utiliza la tecnica del Ray Tracing.
Dos modelos son utilizados IRI y el Ray_Tracing (en Fortran)

Se definen parametros como:
      Camino de propagacion
      Retardo
      Rango Oblicuo
      Rango Terrestre
    

Created on Fri May 10 10:46:53 2021
@author: Zenon Saavedra
"""

import os
import sys

import numpy as np
import matplotlib.pyplot as plt
import scipy 
import pandas

import math 
import math as pi
import Confi_Trazador
from matplotlib import cm


class Posicion_Geo():
    def __init__(Pos,Latitud,Longitud,Altitud):
        Pos.Latitud = Latitud
        Pos.Longitud = Longitud
        Pos.Altitud = Altitud
  
def Esfe2xyz(va,az,d):
    va = np.radians(va)
    az = np.radians(az)
    sinv = np.sin(va)
    cosv = np.cos(va)
    sina = np.sin(az)
    cosa = np.cos(az)
    x = d*cosv*cosa
    y = d*cosv*sina
    z = d*sinv
    return x,y,z

def Rango_Ground(lat_tx,lon_tx,lat_final,lon_final):
    """
    Determina el Rango Terrestre seguido por la O.E.
    float RangoGround(float lat_tx, float lon_tx, float lat_final, float lon_final)
    input:
        lat_tx: Latitud del Transmisor (º)
        lon_tx: Longitud del Transmisor (º)
        lat_final: Latitud alcanzada con el RT (º)
        lon_final: Longitud alcanzada con el RT(º)
        
    output:
        Range: Range ground between Rx position and RT position  [m]
    """
    lat_tx_r = math.radians(lat_tx);lon_tx_r = math.radians(lon_tx)
    lat_final_r = math.radians(lat_final);lon_final_r = math.radians(lon_final)    
    
    Re = 6371e3 # Radio de la tierra (m)
    aux = (math.sin((lat_final_r-lat_tx_r)/2))**2 + math.cos(lat_tx_r)*math.cos(lat_final_r)*(math.sin((lon_final_r-lon_tx_r)/2))**2 
    Range = 2 * Re * math.asin(math.sqrt(aux))
    
    return Range

def Trazador_Rayos(Lat_Tx, Long_Tx, Altitud_Tx, frec, elev, azim, Anio, Fecha, UTI, Hora,plot):
    """
    Determina el camino de propagacion de la O.E y una serie de parametros
    relacionados con ello
        
    float Trazo_Rayos(float fc,float Lat_Tx, float Lon_Tx,string Fecha,float Rz)
        Entrada:
            fc: Frec. de Portadora[Hz]
            Lat_Tx: Latitud del Tx [º decimales]
            Lon_Tx: Longitud del Tx [º decimales]
            Fecha: dia mes anio [ddmmaa]
            Rz: Numero de manchas solares
            Ang_Elev: 
            Ang_Azi:
            plot: Si se desea realilzar el ploteo de la Ray Tracing
        Salida: 
            Retardo: Ratardo de la O.E (ida) [s]
            Rango_Terrestre: Distancia medida sobre la tierra [m]
            Rango_Oblicuo: Distancia seguida por la O:E [m]
            Atte_Des: Atenuacion con desviación 
            Lat_Obj: Latitud del Objetivo [º decimales]
            Lon_Obj: Longitud del Objetivo [º decimales]
            Alt_Obj: Altitud del Objetivo [m]
    """
        
    
    os.getcwd()
    
    
 
    os.chdir(r"C:\Users\54381\Desktop\Proyecto\Ray_Trancing\ray_tracing\dist\Release\Cygwin_1-Windows")

    #Lat_Tx = -42.28 # Latitud Geo.
    #Long_Tx = -63.4 # Longitud Geo.
    #Altitud_Tx = 0 
    #frec = 5e6 # Hz
    #elev = 6
    #azim = 98
    #Anio = 2010
    #Fecha = "0516"
    #UTI = 0
    #Hora = 15
    
    #==============================================================================
    Confi_Trazador.Configuracion_IRI(Anio, Fecha, UTI, Hora)
    
    #==============================================================================
    Confi_Trazador.Configuracion_RAY(Lat_Tx, Long_Tx, Altitud_Tx, frec, elev, azim)
    
    #==============================================================================
    #print ("Inicio de Ray tracing \n")
    
                                     
    os.system("ray_tracing.exe")
    
    
    with open ('raytracing.txt',"r") as f:
        coord = f.readlines()
    
    N = np.size(coord)
    aux = []
    for i in np.arange(N):    
        aux.append(coord[i].split())
    
    pos = np.array(aux).astype(float)
    G = np.where((np.diff(pos[:,0]) != 0) & (np.diff(pos[:,1]) != 0) & (np.diff(pos[:,2]) != 0) )
    g = np.asarray(G).transpose()
    
    
    Retardo = pos[-1,0]/1e3
    Rango_Oblicuo = pos[-1,1]*1e3
    
    rho = pos[g,0]
    phi = pos[g,1]
    theta = pos[g,2]
    
    radio = rho * 1E3
    Lat = np.degrees((math.pi/2) - phi)
    Lon = np.degrees(theta)
    Alt = (radio - 6.371E6)
    
    Lat_Final = Lat[-1]
    Lon_Final = Lon[-1]
    Alt_Final = Alt[-1]
    
    
    Rango_Terrestre = Rango_Ground(Lat_Tx,Long_Tx,Lat_Final.item(),Lon_Final.item())
    
       
    if (plot == True) :
        R = radio
        PHI,THETA = np.meshgrid(np.radians(phi),np.radians(theta))
        X = R * np.cos(PHI) * np.sin(THETA)
        Y = R * np.sin(PHI) * np.sin(THETA)
        Z = R * np.cos(THETA)
        
        fig = plt.figure()
        ax = fig.add_subplot(projection = '3d')
        surf = ax.plot_surface(X,Y, (Z- 6.371E6)/1E3, rstride=1, cstride=1, cmap=cm.jet,
                linewidth=0, antialiased=False)
        

        ax.plot3D(X.ravel()[0],Y.ravel()[0],(Z.ravel()[0]-6.371E6)/1e3, '2',mew = 12,label = "Tx")
        ax.legend()
        
        Pos_Lon_med = int(len(Lon)/2); Pos_Lat_med = int(len(Lat)/2)
        
        Lon_min = round(Long_Tx,2); Lon_max = round(Lon_Final,2); Lon_med = round(float(Lon[Pos_Lon_med]),2) 
        ax.set_yticks([Y[0,0],Y[Pos_Lon_med, Pos_Lon_med], Y[-1,-1]])
        ax.set_yticklabels([Lon_min, Lon_med,Lon_max])
        ax.set_xticks([X[0,0], X[Pos_Lat_med,Pos_Lat_med], X[-1,-1]])
        Lat_min = round(Lat_Tx,2); Lat_max = round(Lat_Final,2); Lat_med = round(float(Lon[Pos_Lat_med]),2)
        ax.set_xticklabels([Lat_min,Lat_med,Lat_max])
        ax.set_zlabel("Altitud (km)")
        
        ax.set_xlabel("Latitud ($\\degree$)")
        ax.set_ylabel("Longitud ($\\degree$)")
    plt.show()
    os.chdir(r"C:\Users\54381\Desktop\Proyecto\Radar_OTH\ray_tracing\dist\Release\Cygwin_1-Windows")


    return Retardo, Rango_Terrestre, Rango_Oblicuo, Lat_Final, Lon_Final, Alt_Final


def main():
    print(f'\n')
    print(f'=============Inicio============')
    Lat_Tx = -42.28 # Latitud Geografica [º decimales]
    Lon_Tx = -63.4 # Longitud Geografica [º decimales]
    Alt_Tx = 0 # m 
    
    Posicion_Tx = Posicion_Geo(Lat_Tx,Lon_Tx,Alt_Tx)       
    
    Hora = 15 # Hora 24 hs
    UTI = 0
    Fecha = "15-06-2010" # ddmmaa
    dia,mes,anio = Fecha.split("-")
    Anio = float(anio)
    mmdd = mes + dia
    elev = 5
    azim = 98
    Tipo_zona = "Rural"    #'Comercial' 'Residencial' 'Rural' 'Rural Tranquila'

    fc = 10e6 # Hz
    AB = 10e3 # Hz
    
    [Retardo, Rango_Terrestre, Rango_slant, Lat_Final,Lon_Final, Alt_Final] = Trazador_Rayos(
        Posicion_Tx.Latitud,Posicion_Tx.Longitud,Posicion_Tx.Altitud,
        fc, elev, azim, Anio, mmdd, UTI, Hora,plot=False) 
    
        
    print('===============================\n')
    print(f"Rango_slant: {Rango_slant/1e3: 2.2f}")
    print(f"Retardo: {Retardo*1e3: 2.2f}")
    print(f"Rango_ground: {Rango_Terrestre/1e3: 2.2f}")
    print(f"f carrier: {fc/1e6: 2.2f}")
    
    return 




# INICIO    
if __name__ == '__main__':
    main()




# Z = np.array([(5,6,7),(1,2,3)])
# A = np.array([[0],[1],[2]]) # array (3,1)
# B = A.ravel() # conviente array (3,1) --> (3,) array 1D
# C = np.array([B]).transpose() #convierte array 1D (3,) --> (3,1)
# D = A.reshape(-1) # conviente array (3,1) --> (3,) array 1D
# H = np.array([[0,1,2],[3,4,5],[6,7,8]]) # array (3,1)
# F = H.flatten() # (3,3) --> (9,) 1D

# print(Z)
# print(np.shape(Z.T))
# print(np.shape(Z))


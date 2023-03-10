# -*- coding: utf-8 -*-
"""
Created on Tue Nov 16 14:00:50 2021

@author: arw
"""

import os
import cdsapi
import zipfile
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.offsetbox import (OffsetImage, AnnotationBbox)
import xarray as xr
import matplotlib as mpl
import matplotlib.colors as colors
import matplotlib.ticker as ticker
import matplotlib.image as image
import matplotlib.pyplot as plt
import numpy as np
from netCDF4 import Dataset, num2date
from cartopy.feature import ShapelyFeature
from shapely.geometry import Polygon
import shapely.affinity
import numpy as np
import pandas as ps
import geopandas as gpd


#Cambio al directorio de trabajo
os.chdir('/home/arw/scripts/python/cams/temp')

import datetime
yesterday = datetime.date.fromordinal(datetime.date.today().toordinal()-1).strftime("%F")
string = f'{yesterday}/{yesterday}'

ahora = datetime.datetime.now()
hoy = ahora.strftime("%d/%m/%Y %H:%M:%S")
etiqueta_hora = "Hora de creación: "+hoy+"Hora local"

#Script para analizar la 
#------------------------------------------------------------------>
c = cdsapi.Client()

c.retrieve(
    'cams-global-atmospheric-composition-forecasts',
    {
        'variable': [
            'dust_aerosol_optical_depth_550nm', 'particulate_matter_10um', 'particulate_matter_2.5um',
        ],
        #'date': '2022-10-23/2022-10-23',
        'date': string,
        'time': '12:00',
        'leadtime_hour': [
            '24', '25', '26',
            '27', '28', '29',
            '30', '31', '32',
            '33', '34', '35',
            '36', '37', '38',
            '39', '40', '41',
            '42', '43', '44',
            '45', '46', '47',
            '48', '49', '50',
            '51', '52', '53',
            '54', '55', '56',
            '57', '58', '59',
            '60', '61', '62',
            '63', '64', '65',
            '66', '67', '68',
            '69', '70', '71',
            '72', '73', '74',
            '75', '76', '77',
            '78', '79', '80',
            '81', '82', '83',
            '84', '85', '86',
            '87', '88', '89',
            '90',
        ],
        'type': 'forecast',
        'area': [
            15.4, -91.3, 12,
            -86.3,
        ],
        'format': 'netcdf_zip',
    },
    'download.netcdf_zip')
#------------------------------------------------------------------>
#Descomprime el archivo descargado
archivo_zip = zipfile.ZipFile("download.netcdf_zip")
archivo_zip.extractall()

#Leemos el netcdf que acabamos de bajar
nc = Dataset('data.nc')

#Borra archivos temporalaes
os.remove("download.netcdf_zip")
os.remove("data.nc")

#Inventario del contenido del archivo 1
#for key,value in nc.variables.items():
#    print(key)
#    print(value)
#    print()
    
    
#Lectura de latitudes y longitudes
lat = nc.variables['latitude'][:]
zlon = nc.variables['longitude'][:]    

X,Y = np.meshgrid(zlon,lat)

#Lectura de niveles (Si los hubiere)
#nivel = nc.variables['level'][:]

shp = gpd.read_file('/home/arw/shape/ESA_CA_wgs84.shp')
logo = image.imread("/home/arw/scripts/python/cams/logoMarn_color.png")
icca = image.imread("/home/arw/scripts/python/cams/ICCA.jpeg")

#Construyendo el vector de tiempos
#Lectura y formato del tiempo
unidades = nc.variables['time'].units
calendario = nc.variables['time'].calendar
tiempo = nc.variables['time'][:]-6
tiempo = num2date(tiempo, units=unidades,calendar=calendario)
tiempo = [i.strftime("%d-%m-%Y %H:%M") for i in tiempo]


#Se setean los limites
levels_pm10 = np.arange(0.00000001,0.00000006,0.000000001)
levels_pm25 = np.arange(0.00000001,0.00000005,0.000000001)

#Lectura de variables, en este caso, contaminantes (Se omite el nivel porque no hay)
pm10 = nc.variables['pm10'][:,:,:]*1000000000
#pm10 = nc.variables['pm10'][:,:,:]*1000000000000
pm25 = nc.variables['pm2p5'][:,:,:]*1000000000
itime=len(tiempo)-1 #Asumo que el vector comienza en 0

#------------------------------------------------------------------------------------------------------------------------->
#Defino los colores y categorias
paleta=['#92d14f', '#ffff01', '#ffc000','#fe0000','#7030a0','#000000','#000000']
niveles_pm10_icca = [56,155,255,355,424,604]
niveles_pm25_icca = [15.5,40.5,66,160,251,500]
niveles_pm10 = range(0,100,1)
niveles_pm25 = range(0,50,1)
categorias = ['Buena','Moderada','Dañina sensibles','Dañina salud','Muy dañina','Peligroso']
#------------------------------------------------------------------------------------------------------------------------->

#------------------------------------------------------------------------------------------------------------------------->
#MAPA CON COLORES Y DATOS SIN ICCA
#Plot PM10
for i in range (itime):
    variable = pm10[i,:,:]
    #Creo una figura con subplots de tamaño 12 y 10
    fig, ax = plt.subplots(figsize=(12,10))
    
    #Creo el contorno usando la malla de puntos de latitudes y longitudes junto con la variable a dibujar
    cont = ax.contourf(X,Y, variable, extend='both', cmap='YlOrBr', levels=niveles_pm10)

    #Añado la barra de colores al objeto ax de 12 y 10
    cbar = fig.colorbar(cont, fraction=0.04, pad=0.04, shrink=0.70 , extendrect=False, orientation='horizontal')    
    #cont.set_clim(0, 250)
    #cbar.set_ticklabels(categorias)
    
    #Se añade un titulo
    ax.set_title('Pronóstico de PM 10 (microgramos/metro cúbico) para: \n\n %s' % tiempo[i] + " Hora local \n\n Modelo cams-global-atmospheric-composition-forecasts" + "\n Dirección del observatorio de amenazas y recursos naturales - MARN \n" )
    #ax.set_title(texto, fontsize=10, color="white")
    #Etiqueta para el eje x
    ax.set_xlabel("Longitud", fontsize=6, loc='right')
    #Etiqueta para el eje y
    ax.set_ylabel("Latitud", fontsize=6)
    #Se fijan los límites en y con los valores mínimos y máximos de latitud
    ax.set_ylim(min(lat),max(lat))
    #Se fijan los límites en y con los valores mínimos y máximos de longitud
    ax.set_xlim(min(zlon),max(zlon))
    #Se dibuja el grid
    plt.grid()
    #Se dibuja el layout
    plt.tight_layout()
    #Se dibuja el shape
    shp.plot(ax=ax, color='black', linewidth=0.5)
    #Se añade el logo
    newax = fig.add_axes([0.8, 0.9, 0.21, 0.75], anchor='SE')
    newax.imshow(logo)
    #Le añado una etiqueta
    newax.text(75, 450,etiqueta_hora, fontsize=6)
    plt.axis("off")
    fig.savefig("cams_pm10_"+f'{i}'+".png")
    matplotlib.pyplot.close()
#------------------------------------------------------------------------------------------------------------------------->

#------------------------------------------------------------------------------------------------------------------------->
#Plot PM2.5
for i in range (itime):
    variable = pm25[i,:,:]
    #Creo una figura con subplots de tamaño 12 y 10
    fig, ax = plt.subplots(figsize=(12,10))
    
    #Creo el contorno usando la malla de puntos de latitudes y longitudes junto con la variable a dibujar
    cont = ax.contourf(X,Y, variable, extend='both', cmap='YlOrBr', levels=niveles_pm25)

    #Añado la barra de colores al objeto ax de 12 y 10
    cbar = fig.colorbar(cont, fraction=0.04, pad=0.04, shrink=0.70 , extendrect=False, orientation='horizontal')    
    #Se añade un titulo
    ax.set_title('Pronóstico de PM 2.5 (microgramos/metro cúbico) para: \n\n %s' % tiempo[i] + " Hora local \n\n Modelo cams-global-atmospheric-composition-forecasts" + "\n Dirección del observatorio de amenazas y recursos naturales - MARN \n" )
    #ax.set_title(texto, fontsize=10, color="white")
    #Etiqueta para el eje x
    ax.set_xlabel("Longitud", fontsize=6, loc='right')
    #Etiqueta para el eje y
    ax.set_ylabel("Latitud", fontsize=6)
    #Se fijan los límites en y con los valores mínimos y máximos de latitud
    ax.set_ylim(min(lat),max(lat))
    #Se fijan los límites en y con los valores mínimos y máximos de longitud
    ax.set_xlim(min(zlon),max(zlon))
    #Se dibuja el grid
    plt.grid()
    #Se dibuja el layout
    plt.tight_layout()
    #Se dibuja el shape
    shp.plot(ax=ax, color='black', linewidth=0.5)
    #Se añade el logo
    newax = fig.add_axes([0.8, 0.9, 0.19, 0.75], anchor='SE')
    newax.imshow(logo)
    #Le añado una etiqueta
    newax.text(75, 450,etiqueta_hora, fontsize=6)
    plt.axis("off")
    fig.savefig("cams_pm25_"+f'{i}'+".png")
    matplotlib.pyplot.close()

#------------------------------------------------------------------------------------------------------------------------->

#MAPAS CON ICCA

#------------------------------------------------------------------------------------------------------------------------->
#Plot PM10
for i in range (itime):
    variable = pm10[i,:,:]
    #Creo una figura con subplots de tamaño 12 y 10
    fig, ax = plt.subplots(figsize=(12,10))
    
    #Creo el contorno usando la malla de puntos de latitudes y longitudes junto con la variable a dibujar
    cont = ax.contourf(X,Y, variable, extend='both', colors=paleta, levels=niveles_pm10_icca)

    #Añado la barra de colores al objeto ax de 12 y 10
    cbar = fig.colorbar(cont, fraction=0.04, pad=0.04, shrink=0.70 , extendrect=False, orientation='horizontal')    
    cont.set_clim(0, 600)
    cbar.set_ticklabels(categorias)

    #Se añade un titulo
    ax.set_title('Pronóstico de la calidad del aire para: \n\n  %s' % tiempo[i] + " Hora local \n\n Modelo cams-global-atmospheric-composition-forecasts" + "\n Dirección del observatorio de amenazas y recursos naturales - MARN \n" )
    #ax.set_title(texto, fontsize=10, color="white")
    #Etiqueta para el eje x
    ax.set_xlabel("Longitud", fontsize=6, loc='right')
    #Etiqueta para el eje y
    ax.set_ylabel("Latitud", fontsize=6)
    #Se fijan los límites en y con los valores mínimos y máximos de latitud
    ax.set_ylim(min(lat),max(lat))
    #Se fijan los límites en y con los valores mínimos y máximos de longitud
    ax.set_xlim(min(zlon),max(zlon))
    #Se dibuja el grid
    plt.grid()
    #Se dibuja el layout
    plt.tight_layout()
    #Se dibuja el shape
    shp.plot(ax=ax, color='black', linewidth=0.5)
    #Se añade el logo
    newax = fig.add_axes([0.8, 0.9, 0.19, 0.75], anchor='SE')
    newax.imshow(logo)
    #Le añado una etiqueta
    newax.text(75, 450,etiqueta_hora, fontsize=6)
    plt.axis("off")
    #Se añade la imagen de detalles
    newax_2 = fig.add_axes([0.066, 0.12, 0.32, 0.32], anchor='SE')
    newax_2.imshow(icca)
    plt.axis("off")
    fig.savefig("cams_pm10_icca_"+f'{i}'+".png")
    matplotlib.pyplot.close()
#------------------------------------------------------------------------------------------------------------------------->

#------------------------------------------------------------------------------------------------------------------------->
#Plot PM2.5
for i in range (itime):
    variable = pm25[i,:,:]
    #Creo una figura con subplots de tamaño 12 y 10
    fig, ax = plt.subplots(figsize=(12,10))
    
    #Creo el contorno usando la malla de puntos de latitudes y longitudes junto con la variable a dibujar
    cont = ax.contourf(X,Y, variable, extend='both', colors=paleta, levels=niveles_pm25_icca)

    #Añado la barra de colores al objeto ax de 12 y 10
    cbar = fig.colorbar(cont, fraction=0.04, pad=0.04, shrink=0.70 , extendrect=False, orientation='horizontal')    
    cont.set_clim(0, 500)
    cbar.set_ticklabels(categorias)
        
    #Le añado una etiqueta
    #Se añade un titulo
    ax.set_title('Pronóstico de la calidad del aire para: \n\n %s' % tiempo[i] + " Hora local \n\n Modelo cams-global-atmospheric-composition-forecasts" + "\n Dirección del observatorio de amenazas y recursos naturales - MARN \n" )
    #Etiqueta para el eje x
    ax.set_xlabel("Longitud", fontsize=6, loc='right')
    #Etiqueta para el eje y
    ax.set_ylabel("Latitud", fontsize=6)
    #Se fijan los límites en y con los valores mínimos y máximos de latitud
    ax.set_ylim(min(lat),max(lat))
    #Se fijan los límites en y con los valores mínimos y máximos de longitud
    ax.set_xlim(min(zlon),max(zlon))
    #Se dibuja el grid
    plt.grid()
    #Se dibuja el layout
    plt.tight_layout()
    #Se dibuja el shape
    shp.plot(ax=ax, color='black', linewidth=0.5)
    #Se añade el logo
    newax = fig.add_axes([0.8, 0.9, 0.19, 0.75], anchor='SE')
    newax.imshow(logo)
    #Le añado una etiqueta
    newax.text(75, 450,etiqueta_hora, fontsize=6)
    plt.axis("off")
    #Se añade la imagen de detalles
    newax_2 = fig.add_axes([0.066, 0.12, 0.35, 0.35], anchor='SE')
    newax_2.imshow(icca)
    plt.axis("off")
    fig.savefig("cams_pm25_icca_"+f'{i}'+".png")
    matplotlib.pyplot.close()
#------------------------------------------------------------------------------------------------------------------------->
##################################################################
#graficas2.py (nombre temporal)
#Autor: Tomas Galvez
#Para: CEAB, UVG, Guatemala
#Creado en septiembre 2018
#Última modificación: 29/10/2018
#
#Módulo de funciones para generación de gráficas univariable en
#HTML con matplotlib y mpld3.
#
#Copyright (C) 2018  Tomas Gálvez P.
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.
##################################################################

#import io
#import base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as pyplt
from mpld3 import plugins, fig_to_html
import pandas as pd
from testing import debugPrint
from os import getcwd

#Construye un Data Frame de Pandas usando los resultados de una consulta a la DB. Es importante notar que supone resultados con dos campos únicamente, y que el primero es el de la variable independiente.
def rowsToDataFrame(campo, rows, xName = 'Date', per = 'Por hora'):
    x = []
    y = []
    for row in rows:
        x.append(row[0])
        y.append(row[1])

    df = pd.DataFrame({xName : x, campo : y})

    if (per == 'Por día'):
        df = df.groupby(xName, as_index = False).agg({campo:'mean'})
        debugPrint("Agrupacion exitosa")
        debugPrint(df.keys())
    elif (per == 'Por mes'):
        df = df.groupby(xName, as_index = False).agg({campo:'mean'})
        debugPrint("Agrupacion exitosa")
        debugPrint(df.keys())
    return df

#Produce un CSV a partir del data frame y el nombre de archivo provistos. Se hace aquí porque aquí tenemos acceso a Pandas.
def dfToCSV(df, filename):
    directory = getcwd() + '\\descargas\\' + filename + '.csv'
    df.to_csv(directory)

#----Funciones para hacer gráficas univariable----
def plotConPlugins(fig):#, plot=None):
    #debugPrint("El parametro plot contiene " + str(plot[0]))
    plugins.connect(fig, plugins.BoxZoom(button = False))#, plugins.PointLabelTooltip(plot[0]))
    debugPrint("Se logro conectar el plugin BoxZoom")
    plot_url = fig_to_html(fig)

    debugPrint("A punto de cerrar la figura")
    pyplt.close(fig)

    return plot_url

def plotear(df, campo, scatter = True, xName = 'Date'):
    #img = io.BytesIO()
    #pyplt.clf()
    fig = pyplt.figure()
    #pyplt.xticks(rotation = 'vertical')

    if (scatter):
        p = pyplt.plot(df[xName], df[campo], 'b.') #Se usa un format string para especificar la necesidad de una scatter plot.
    else:
        p = pyplt.plot(df[xName], df[campo])

    debugPrint("Antes de mostrar el contenido de fig")
    debugPrint(fig)
    debugPrint("Despues de mostrar el contenido de fig")

    #pyplt.savefig(img, format = 'png')
    #img.seek(0)

    #plot_url = base64.b64encode(img.getvalue()).decode()
    
    return plotConPlugins(fig)#, p)


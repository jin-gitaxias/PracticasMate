##################################################################
#graficas2.py (nombre temporal)
#Autor: Tomas Galvez
#Para: CEAB, UVG, Guatemala
#Creado en septiembre 2018
#Última modificación: 11/09/2018
#
#Módulo de funciones para generación de gráficas univariable en
#HTML con matplotlib y mpld3.
##################################################################

#import io
#import base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as pyplt
from mpld3 import plugins, fig_to_html
import pandas as pd
from testing import debugPrint

#Construye un Data Frame de Pandas usando los resultados de una consulta a la DB. Es importante notar que supone resultados con dos campos únicamente, y que el primero es el de la variable independiente.
def rowsToDataFrame(campo, rows, xName = 'Date'):
    x = []
    y = []
    for row in rows:
        x.append(row[0])
        y.append(row[1])

    df = pd.DataFrame({xName : x, campo : y})
    return df

#----Funciones para hacer gráficas univariable por hora, día y mes----
def plotConPlugins(fig):#, plot=None):
    #debugPrint("El parametro plot contiene " + str(plot[0]))
    plugins.connect(fig, plugins.BoxZoom(button = False))#, plugins.PointLabelTooltip(plot[0]))
    debugPrint("Se logro conectar el plugin BoxZoom")
    plot_url = fig_to_html(fig)

    debugPrint("A punto de cerrar la figura")
    pyplt.close(fig)

    return plot_url
    
def plotPorHora(df, campo, scatter = True, xName = 'Date'):
    #img = io.BytesIO()

    #pyplt.clf()
    fig = pyplt.figure()
    #pyplt.xticks(rotation = 'vertical')
    if (scatter):
        pyplt.plot(df[xName], df[campo], 'b.') #Se usa un format string para especificar la necesidad de una scatter plot.
    else:
        pyplt.plot(df[xName], df[campo])

    #pyplt.savefig(img, format = 'png')
    #img.seek(0)

    #plot_url = base64.b64encode(img.getvalue()).decode()
    #pyplt.close(fig)

    debugPrint("Antes de ejecutar plotConPlugins en plotPorHora")

    return plotConPlugins(fig)
    #return plot_url

def plotPorDia(df, campo, xName = 'Date'):
    #img = io.BytesIO()

    df_resumido_por_dia = df.groupby(xName, as_index = False).agg({campo:'mean'})
    debugPrint("Agrupacion exitosa")
    debugPrint(df_resumido_por_dia.keys())

    #pyplt.clf()
    fig = pyplt.figure()
    #pyplt.xticks(rotation = 'vertical')
    debugPrint("Antes de mostrar el contenido de fig")
    debugPrint(fig)
    debugPrint("Despues de mostrar el contenido de fig")
    p = pyplt.plot(df_resumido_por_dia[xName], df_resumido_por_dia[campo])
    #pyplt.savefig(img, format = 'png')
    #img.seek(0)

    #plot_url = base64.b64encode(img.getvalue()).decode()
    
    return plotConPlugins(fig)#, p)

def plotPorMes(df, campo, xName = 'Date'):
    #img = io.BytesIO()
    
    df_resumido_por_mes = df.groupby(xName, as_index = False).agg({campo:'mean'})
    debugPrint("Agrupacion exitosa")
    debugPrint(df_resumido_por_mes)

    #pyplt.clf()
    fig = pyplt.figure()
    #pyplt.xticks(rotation = 'vertical')
    pyplt.plot(df_resumido_por_mes[xName], df_resumido_por_mes[campo])
    #pyplt.savefig(img, format = 'png')
    #img.seek(0)

    #plot_url = base64.b64encode(img.getvalue()).decode()

    return plotConPlugins(fig)


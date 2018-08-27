##################################################################
#graficadorSencillo.py
#Autor: Tomas Galvez
#Para: CEAB, UVG, Guatemala
#Creado en agosto 2018
#Última modificación: 24/08/2018
#
#Aplicación FLASK para probar generación de gráficas de data
#meteorológica usando el módulo graficas.py.
##################################################################

from flask import Flask, url_for, render_template, request
from graficas import *

app = Flask(__name__)
#app.config['SERVER_NAME'] = '127.0.0.1:5000/'

conn = connect()

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/graficador', methods = ['GET'])
@app.route('/graficador#grafica', methods = ['GET'])
def graficador():
    name = ""
    tabla = ""
    if ("nombre" in request.args):
        name = request.args['nombre']

    if ("table" in request.args):
        tabla = request.args['table']

    tablas = getTables(conn)

    if tabla == "":
        tabla = tablas[0]
    
    variables = []
    for v in getColumns(conn, tabla):
        if v[1] in ['float4']:
            variables.append(v[0])
    periodos = ['Por hora', 'Por día', 'Por mes']
    variable = ""
    periodo = ""

    try:
        variable = request.args['xvar']
        periodo = request.args['yvar']
        debugPrint("La xvar es " + variable)
        debugPrint("La yvar es " + periodo)

        
        grafica = graficar(variable, periodo)
        debugPrint("Grafica generada\n")

        return render_template('graficador.html', nombre = name, variables = variables, periodos = periodos, tablas = tablas,
                               tabla = tabla,
                               periodo = periodo,
                               variable = variable,
                               graficamos = grafica)
    except Exception as err:
        debugPrint("Hubo excepcion al intentar graficar\n")
        debugPrint(err)
        return render_template('graficador.html', nombre = name, variables = variables, periodos = periodos, tablas = tablas,
                               tabla = tabla,
                               periodo = periodo,
                               variable = variable)

def graficar(variable, periodo):
    resultado = None
    if (periodo == 'Por hora'):
        debugPrint("Si agarramos onda\n")
        qHora = armarQuery('X..Date', variable, '2014-2018SanJacinto')
        debugPrint("El query es " + qHora)
        rHora = query(conn, qHora)

        if rHora is not None:
            debugPrint("Obtuvimos resultados rHora por la gracia de Dios")
            dfD = rowsToDataFrame(variable, rHora)
            debugPrint("Obtuvimos data frame rHora por la gracia de Dios")
            resultado = plotPorHora(dfD, variable)
            debugPrint("Obtuvimos plot rHora por la gracia de Dios")
        else:
            debugPrint("Sadness")
    elif (periodo == 'Por día'):
        qDia = armarQuery('X..Date', variable, '2014-2018SanJacinto')
        rDia = query(conn, qDia)

        if rDia is not None:
            dfD = rowsToDataFrame(variable, rDia)
            resultado = plotPorDia(dfD, variable)
        else:
            debugPrint("Sadness")
    elif (periodo == 'Por mes'):
        qMes = armarQuery('Mes', variable, '2014-2018SanJacinto')
        rMes = query(conn, qMes)

        if rMes is not None:
            dfM = rowsToDataFrame(variable, rMes, 'Mes')
            resultado = plotPorMes(dfM, variable)
        else:
            debugPrint("Sadness")
    else:
        debugPrint("El resultado será None porque no le atinamos al período")
        return None

    #debugPrint("El resultado es " + resultado)
    return resultado

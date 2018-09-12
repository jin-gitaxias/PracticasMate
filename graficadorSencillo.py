##################################################################
#graficadorSencillo.py
#Autor: Tomas Galvez
#Para: CEAB, UVG, Guatemala
#Creado en agosto 2018
#Última modificación: 12/09/2018
#
#Aplicación FLASK para probar generación de gráficas de data
#meteorológica usando el módulo graficas.py.
##################################################################

from flask import Flask, url_for, render_template, request
#from graficas import *
from graficas2 import *
from db import *
from SQLqueries import *
from testing import debugPrint

app = Flask(__name__)
#app.config['SERVER_NAME'] = '127.0.0.1:5000/'

connect()

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/graficador', methods = ['GET'])
@app.route('/graficador#grafica', methods = ['GET'])
def graficador():
    name = tabla = fechaInicial = fechaFinal = ""
    
    if ("nombre" in request.args):
        name = request.args['nombre']

    tablas = getTables()

    if ("table" in request.args):
        tabla = request.args['table']
    else:
        tabla = tablas[0]

    rangoFechas = getRangoFechas(tabla)

    debugPrint("El rango de fechas es " + str(rangoFechas))

    if ("fechai" in request.args and request.args['fechai'] != ""):
        fechaInicial = request.args['fechai']
    else:
        fechaInicial = rangoFechas[0]

    if ("fechaf" in request.args and request.args['fechaf'] != ""):
        fechaFinal = request.args['fechaf']
    else:
        fechaFinal = rangoFechas[1]

    variables = []
    for v in getColumns(tabla):
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

        
        grafica = graficar(variable, periodo, tabla, fechaInicial, fechaFinal)
        debugPrint("Grafica generada\n")

        return render_template('graficador.html', nombre = name, variables = variables, periodos = periodos, tablas = tablas,
                               tabla = tabla,
                               periodo = periodo,
                               variable = variable,
                               fechai = fechaInicial,
                               fechaf = fechaFinal,
                               graficamos = grafica)
    except Exception as err:
        debugPrint("Hubo excepcion al intentar graficar\n")
        debugPrint(err)
        return render_template('graficador.html', nombre = name, variables = variables, periodos = periodos, tablas = tablas,
                               tabla = tabla,
                               periodo = periodo,
                               variable = variable,
                               fechai = fechaInicial,
                               fechaf = fechaFinal)

def formatDate(y, m, d):
    return str(y) + "-" + str(int(m / 10)) + str(m % 10) + "-" + str(int(d / 10)) + str(d % 10)

def getRangoFechas(table):
    resultado = None
    q = armarQuery(table, "datefield")
    rq = query(q)

    if rq is not None:
        fechaMenor = rq[0][0]
        fechaMayor = rq[len(rq) - 1][0]
        debugPrint("La fecha menor es " + str(type(rq[0][0])))
        
        resultado = [formatDate(fechaMenor.year, fechaMenor.month, fechaMenor.day),
                     formatDate(fechaMayor.year, fechaMayor.month, fechaMayor.day)]

    return resultado
    
def graficar(variable, periodo, tabla, fechai = None, fechaf = None):
    resultado = None
    if (fechai is not None):
        fechai = castFecha(fechai)
    if (fechaf is not None):
        fechaf = castFecha(fechaf)
    if (periodo == 'Por hora'):
        debugPrint("Si agarramos onda\n")
        qHora = armarQuery(tabla, 'datetimefield', variable, armarWhereRangoFechas(fechai, fechaf))
        debugPrint("El query es " + qHora)
        rHora = query(qHora)

        if rHora is not None:
            debugPrint("Obtuvimos resultados rHora por la gracia de Dios")
            dfD = rowsToDataFrame(variable, rHora)
            debugPrint("Obtuvimos data frame rHora por la gracia de Dios")
            resultado = plotPorHora(dfD, variable)
            debugPrint("Obtuvimos plot rHora por la gracia de Dios")
        else:
            debugPrint("Sadness 1")
    elif (periodo == 'Por día'):
        debugPrint("Entramos a 'Por día'")
        qDia = armarQuery(tabla, 'datefield', variable, armarWhereRangoFechas(fechai, fechaf))
        debugPrint("El query es " + qDia)
        debugPrint("Se hizo el query en Por día")
        rDia = query(qDia)
        debugPrint("Se envio el query en Por día")

        if rDia is not None:
            dfD = rowsToDataFrame(variable, rDia)
            debugPrint("A punto de ejecutar plotPorDia")
            resultado = plotPorDia(dfD, variable)
        else:
            debugPrint("Sadness 2")
    elif (periodo == 'Por mes'):
        qMes = armarQuery(tabla, 'monthfield', variable, armarWhereRangoFechas(fechai, fechaf))
        debugPrint("El query es " + qMes)
        rMes = query(qMes)

        if rMes is not None:
            dfM = rowsToDataFrame(variable, rMes)
            resultado = plotPorMes(dfM, variable)
        else:
            debugPrint("Sadness 3")
    else:
        debugPrint("El resultado será None porque no le atinamos al período")
        return None

    #debugPrint("El resultado es " + resultado)
    return resultado

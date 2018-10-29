##################################################################
#graficadorSencillo.py
#Autor: Tomas Galvez
#Para: CEAB, UVG, Guatemala
#Creado en agosto 2018
#Última modificación: 29/10/2018
#
#Aplicación FLASK para probar generación de gráficas de data
#meteorológica usando el módulo graficas.py.
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

from flask import Flask, url_for, render_template, request, send_from_directory
from werkzeug.utils import secure_filename
from graficas import *
from db import *
from SQLqueries import *
from testing import debugPrint
from os import getcwd

app = Flask(__name__)
#app.config['SERVER_NAME'] = '127.0.0.1:5000/'

connect()

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/graficador/<filename>')
def download(filename):
    downloads = getcwd() + "\\descargas\\"
    return send_from_directory(directory=downloads, filename = filename, mimetype = 'text/csv', as_attachment = True)

@app.route('/graficador', methods = ['GET'])
@app.route('/graficador#grafica', methods = ['GET'])
def graficador():
    periodos = ['Por hora', 'Por día', 'Por mes']
    filenameForDownload = ""
    
    name, variable, variables, periodo, tabla, tablas, fechaInicial, fechaFinal = getQueryParams()
    debugPrint("Los datos que se obtuvieron son")
    debugPrint(name)
    debugPrint(variable)
    debugPrint(variables)
    debugPrint(periodo)
    debugPrint(tabla)
    debugPrint(tablas)
    debugPrint(fechaInicial)
    debugPrint(fechaFinal)
    
    s = translateToQuery(variable, periodo, tabla, fechaInicial, fechaFinal)

    if (s is not None):
        debugPrint("A punto de crear archivo descargable")
        filenameForDownload = secure_filename(variable + periodo + "De" + fechaInicial + "A" + fechaFinal + tabla)
        try:
            rd = exportFile(s, filenameForDownload)
            debugPrint("Archivo descargable creado. Resultado: " + str(rd))
        except Exception as err:
            debugPrint("Hubo excepcion al intentar crear archivo descargable\n")
            debugPrint(err)
    else:
        debugPrint("s es None")

    try:        
        grafica = graficar(s, periodo, variable)
        debugPrint("Grafica generada\n")

        return render_template('graficador.html', nombre = name, variables = variables, periodos = periodos, tablas = tablas,
                               tabla = tabla,
                               periodo = periodo,
                               variable = variable,
                               fechai = fechaInicial,
                               fechaf = fechaFinal,
                               graficamos = grafica, 
                               filenameForDownload = filenameForDownload)
    except Exception as err:
        debugPrint("Hubo excepcion al intentar graficar\n")
        debugPrint(err)
        return render_template('graficador.html', nombre = name, variables = variables, periodos = periodos, tablas = tablas,
                               tabla = tabla,
                               periodo = periodo,
                               variable = variable,
                               fechai = fechaInicial,
                               fechaf = fechaFinal)
    
def getQueryParams():
    name = tabla = fechaInicial = fechaFinal = variable = periodo = ""
    
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

    if ('xvar' in request.args):
        variable = request.args['xvar']

    if ('yvar' in request.args):
        periodo = request.args['yvar']
    debugPrint("La xvar es " + variable)
    debugPrint("La yvar es " + periodo)

    return(name, variable, variables, periodo, tabla, tablas, fechaInicial, fechaFinal)

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

def translateToQuery(variable, periodo, tabla, fechai = None, fechaf = None):
    q = None
    if (fechai is not None):
        fechai = castFecha(fechai)
    if (fechaf is not None):
        fechaf = castFecha(fechaf)
    if (periodo == 'Por hora'):
        debugPrint("Entramos a 'Por hora'")
        q = armarQuery(tabla, 'datetimefield', variable, armarWhereRangoFechas(fechai, fechaf))
        debugPrint("El query es " + q)
    elif (periodo == 'Por día'):
        debugPrint("Entramos a 'Por día'")
        q = armarQuery(tabla, 'datefield', variable, armarWhereRangoFechas(fechai, fechaf))
        debugPrint("El query es " + q)
    elif (periodo == 'Por mes'):
        debugPrint("Entramos a 'Por mes'")
        q = armarQuery(tabla, 'monthfield', variable, armarWhereRangoFechas(fechai, fechaf))
        debugPrint("El query es " + q)
        
    return q

def graficar(q, per, var):
    resultado = None
    data = query(q)
    if data is not None:
        dfD = rowsToDataFrame(var, data)
        if (per == 'Por hora'):
            resultado = plotPorHora(dfD, var)
        elif (per == 'Por día'):
            resultado = plotPorDia(dfD, var)
        elif (per == 'Por mes'):
            resultado = plotPorMes(dfD, var)
        else:
            debugPrint("El resultado será None porque no le atinamos al período")
            return None
    else:
        debugPrint("Sadness")

    return resultado

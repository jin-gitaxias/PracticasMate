##################################################################
#graficadorSencillo.py
#Autor: Tomas Galvez
#Para: CEAB, UVG, Guatemala
#Creado en agosto 2018
#Última modificación: 14/11/2018
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

from flask import Flask, url_for, render_template, request, send_from_directory, redirect
from werkzeug.utils import secure_filename
from graficas import *
from db import *
from SQLqueries import *
from testing import debugPrint
import subprocess as sp
import os

app = Flask(__name__)
UPLOAD_FOLDER = getcwd() + "\\cargas\\"
ALLOWED_EXTENSIONS = set(['txt', 'csv'])
DOWNLOAD_FOLDER = getcwd() + "\\descargas\\"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
#app.config['SERVER_NAME'] = '127.0.0.1:5000/'

connect()

@app.route('/cargarData', methods = ['POST'])
def cargarData():
    name = ""
    if ("nombre" in request.form):
        name = request.form['nombre']

    try:
        if request.method == 'POST':
            debugPrint('Chequeando que venga el archivo...')
            # check if the post request has the file part
            if 'file' not in request.files:
                debugPrint('No viene archivo')
                return redirect(request.url)
            file = request.files['file']
            # if user does not select file, browser also
            # submit an empty part without filename
            debugPrint('Chequeando que el archivo haya sido seleccionado...')
            if file.filename == '':
                debugPrint('No se ha seleccionado un archivo')
                return redirect(request.url)
            debugPrint('Chequeando si todo bien para proceder...')
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                destino = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(destino)
                sp.check_call(['Rscript', 'migradorDB.R', destino], shell = True)
    except Exception as err:
        debugPrint("Hubo excepcion al intentar obtener los datos\n")
        debugPrint(err)
    finally:
        return redirect('/graficador?nombre=' + name)
    
@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/graficador/descarga/<filename>')
def download(filename):
    return send_from_directory(directory=app.config['DOWNLOAD_FOLDER'], filename = filename, mimetype = 'text/csv', as_attachment = True)

@app.route('/graficador/editVars', methods = ["POST"])
def editVars():
    if ("nombre" in request.form):
        name = request.form['nombre']
        debugPrint("Nombre recibido: " + name)
    if ("variables" in request.form):
        variables = request.form['variables']
        debugPrint("Variables recibidas: " + variables)
        diccionarioVariables = parseDict(variables)
        return render_template('editVars.html', variables = diccionarioVariables, nombre = name)
    else:
        debugPrint("No venían las variables en el request.form")
        return redirect('/graficador?nombre=' + name)

@app.route('/graficador/editVars/go', methods = ["POST"])
def go():
    name = ""
    if "nombre" in request.form:
            name = request.form["nombre"]
            
    if "cancel" not in request.form:
        try:
            dic = parseDict(request.form['variables'])
            debugPrint("El diccionario que se guardará es: " + str(dic))
            with open("prettyVars.txt", 'w', encoding = 'latin-1') as f:
                for key, var in dic.items():
                    if key in request.form:
                        val = request.form[key]
                        debugPrint("Se encontró la clave " + key)
                        if val != "":
                            f.write(key + "->" + val + "\n")
                        else:
                            f.write(key + "->" + key + "\n")
            f.close()
        except Exception as err:
            debugPrint("Ocurrió un problema al guardar los nombres asignados a cada variable")
            debugPrint(err)
        finally:
            return redirect('/graficador?nombre=' + name)
    else:
        return redirect('/graficador?nombre=' + name)

@app.route('/graficador', methods = ['GET'])
@app.route('/graficador#grafica', methods = ['GET'])
def graficador():
    periodos = ['Por hora', 'Por día', 'Por mes']
    filenameForDownload = ""
    
    name, variable, variables, periodo, tabla, tablas, fechaInicial, fechaFinal, scatter = getQueryParams()
    variablesBonitas = {}
    for var in variables:
        variablesBonitas[var] = var
    debugPrint("Los datos que se obtuvieron son")
    debugPrint(name)
    debugPrint(variable)
    debugPrint(variables)
    try:
        with open("prettyVars.txt", encoding = 'latin-1') as f:
            transformaciones = f.read()
        f.close()

        elementos = transformaciones.split("\n")
        for elemento in elementos:
            transf = elemento.split('->')
            if transf[0] in variablesBonitas:
                variablesBonitas[transf[0]] = transf[1]
    except Exception as err:
        debugPrint("Error al leer el archivo de variables bonitas. Se quedan con el nombre original.")
        debugPrint(err)
    debugPrint(variablesBonitas)
    debugPrint(periodo)
    debugPrint(tabla)
    debugPrint(tablas)
    debugPrint(fechaInicial)
    debugPrint(fechaFinal)
    debugPrint(scatter)
    
    s = translateToQuery(variable, periodo, tabla, fechaInicial, fechaFinal)
    df = None

    if (s is not None):
        try:
            df = getData(s, variable, periodo)
        except Exception as err:
            debugPrint("Hubo excepcion al intentar obtener los datos\n")
            debugPrint(err)
            return render_template('graficador.html', nombre = name, variables = variablesBonitas, periodos = periodos, tablas = tablas,
                                       tabla = tabla,
                                       periodo = periodo,
                                       variable = variable,
                                       fechai = fechaInicial,
                                       fechaf = fechaFinal,
                                       scatter = scatter)

        try:
            debugPrint("A punto de crear archivo descargable")
            filenameForDownload = secure_filename(variable + periodo + "De" + fechaInicial + "A" + fechaFinal + tabla)
            dfToCSV(df,filenameForDownload)
            debugPrint("Archivo descargable creado.")
            
        except Exception as err:
            debugPrint("Hubo excepcion al intentar crear archivo descargable\n")
            debugPrint(err)

        finally:
            try:
                df = getData(s, variable, periodo)
                #grafica = plotear(df, variable, scatter = scatter)
                grafica = plotear(df, variable, variablesBonitas[variable], scatter = scatter)
                debugPrint("Grafica generada\n")

                return render_template('graficador.html', nombre = name, variables = variablesBonitas, periodos = periodos, tablas = tablas,
                                       tabla = tabla,
                                       periodo = periodo,
                                       variable = variable,
                                       fechai = fechaInicial,
                                       fechaf = fechaFinal,
                                       scatter = scatter,
                                       graficamos = grafica, 
                                       filenameForDownload = filenameForDownload)
            except Exception as err:
                debugPrint("Hubo excepcion al intentar graficar\n")
                debugPrint(err)
                return render_template('graficador.html', nombre = name, variables = variablesBonitas, periodos = periodos, tablas = tablas,
                                       tabla = tabla,
                                       periodo = periodo,
                                       variable = variable,
                                       fechai = fechaInicial,
                                       fechaf = fechaFinal,
                                       scatter = scatter)
    else:
        debugPrint("s es None")
        return render_template('graficador.html', nombre = name, variables = variablesBonitas, periodos = periodos, tablas = tablas,
                                       tabla = tabla,
                                       periodo = periodo,
                                       variable = variable,
                                       fechai = fechaInicial,
                                       fechaf = fechaFinal,
                                       scatter = scatter)

def parseDict(d):
    d2 = d.strip('{}')
    listaVariables = d2.split(',')
    diccionarioVariables = {}
    for var in listaVariables:
        pedazos = var.split(':')
        pedazos[0] = pedazos[0].strip("' ")
        pedazos[1] = pedazos[1].strip("' ")
        diccionarioVariables[pedazos[0]] = pedazos[1]
    debugPrint("El diccionario que leyó fue: " + str(diccionarioVariables))
    return(diccionarioVariables)

#De http://flask.pocoo.org/docs/1.0/patterns/fileuploads/
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
   
def getQueryParams():
    name = tabla = fechaInicial = fechaFinal = variable = periodo = ""
    scatter = False
    
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

    if ('scatter' in request.args):
        scatter = request.args['scatter']

    return(name, variable, variables, periodo, tabla, tablas, fechaInicial, fechaFinal, scatter)

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

def getData(q, var, per = "Por hora"):
    dfD = None
    data = query(q)

    if data is not None:
        dfD = rowsToDataFrame(var, data, per = per)
    else:
        debugPrint("Sadness")

    return dfD

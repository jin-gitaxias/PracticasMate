##################################################################
#graficas.py
#Autor: Tomas Galvez
#Para: CEAB, UVG, Guatemala
#Creado en agosto 2018
#Última modificación: 29/10/2018
#
#Módulo de funciones para conexión a una base de datos y
#generación de gráficas univariable con matplotlib.
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

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as pyplt
import io
import base64
import psycopg2 as ppg
from configparser import ConfigParser
import pandas as pd
from mpld3 import plugins, fig_to_html

#Esta función permite fácilmente mostrar u ocultar mensajes de debugging mediante comentado de las instrucciones correspondientes.
def debugPrint(s):
    #print(s)
    pass

#Función para importar los datos de conexión a la DB almacenados en el archivo database.ini.
def config(filename='database.ini', section='postgresql'):
    parser= ConfigParser()
    parser.read(filename)

    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return db

#Funcion para conexión a la DB (depende de config()). Devuelve la conexión o None.
def connect():
    conn = None
    cur = None
    try:
        params = config()

        print(params)

        print('Connecting to the PostgreSQL database...')
        conn = ppg.connect(**params)
        cur = conn.cursor()

        print('PostgreSQL database version: ')
        cur.execute('SELECT version()')

        db_version = cur.fetchone()
        print(db_version)

        cur.close()

    except (Exception, ppg.DatabaseError) as error:
        print("Handling connection error...")
        print(error)
    finally:
        if conn is None:
            print('\n\nError connecting to database')
        else:
            print('\n\nConnection succesful')
        return conn

#Para centralizar el nombre del campo de fecha.
def getDateField():
    r = "X..Date"
    return r

#Para centralizar el nombre del campo de meses.
def getMonthField():
    r = "Mes"
    return r

#Arma lo que va despues de WHERE para el caso especifico de fechas.
def armarWhereRangoFechas(fechai = None, fechaf = None):
    s1 = s2 = ""
    if (fechai is not None):
        s1 += '"' + getDateField() + '" >= \'' + fechai + '\'::date'
        if (fechaf is not None):
            s1 += " AND "

    if (fechaf is not None):
        s2 += '"' + getDateField() + '" <= \'' + fechaf + '\'::date'    
    
    return  s1 + s2

#Función para armar queries de dos campos. Su propósito es obtener los ejes para una gráfica univariable.
def armarQuery(tabla, campox, campoy = None, where = None):
    if (campox == "datefield"):
        campox = getDateField()
    elif (campox == "monthfield"):
          campox = getMonthField()

    s = 'SELECT \"' + campox + '\"'

    if (campoy is not None):
        s += ', \"' + campoy + '\"'

    s += ' FROM \"' + tabla + '\"'

    if (where is not None):
        s += " WHERE " + where
    return s

#Realiza un query provisto en el parámetro q. Devuelve el resultado de la consulta o None.
def query(conn, q):
    if conn is not None:
        cur = conn.cursor()
        debugPrint("A punto de ejecutar el query con el nuevo cursor")
        cur.execute(q)
        debugPrint("Se ejecuto el query sin problemas")
        rows = cur.fetchall()
        debugPrint("Se ejecuto el fetchall sin problemas")
        cur.close()
        debugPrint("Se cerro el cursor exitosamente")
        return rows
    else:
        print("Connection is None")
        return None

#Construye un Data Frame de Pandas usando los resultados de una consulta a la DB. Es importante notar que supone resultados con dos campos únicamente, y que el primero es el de la variable independiente.
def rowsToDataFrame(campo, rows, xName = 'Date'):
    x = []
    y = []
    for row in rows:
        x.append(row[0])
        y.append(row[1])

    df = pd.DataFrame({xName : x, campo : y})
    return df

#Obtiene los nombres y tipos de las columnas en la tabla especificada.
def getColumns(conn, table):
    if conn is not None:
        cur = conn.cursor()
        cur.execute("SELECT * FROM \"" + table + "\" LIMIT(0)") #Obtener todo pero sin filas, solo columnas.
        cols = [[desc[0], desc[1]] for desc in cur.description] #desc[1] contiene el OID, para identificar el tipo de columna según PostgreSQL.
        #Se obtiene el nombre del tipo de columna de acuerdo con el OID obtenido en el query anterior.
        for c in cols:
            cur.execute("SELECT pg_type.typname FROM pg_type WHERE pg_type.oid = " + str(c[1]))
            t = cur.fetchone()
            c[1] = t[0]
        cur.close()
        return cols

#Obtiene los nombres de las tablas en la base de datos conectada por medio de conn. Los devuelve en formato de lista.
def getTables(conn):
    if conn is not None:
        cur = conn.cursor()
        cur.execute("""SELECT table_name FROM information_schema.tables
                    WHERE table_schema = 'public'""")
        tablas = list(cur.fetchall()[0])
        cur.close()
        return tablas

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
    pyplt.xticks(rotation = 90)
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
    pyplt.xticks(rotation = 90)
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
    pyplt.xticks(rotation = 90)
    pyplt.plot(df_resumido_por_mes[xName], df_resumido_por_mes[campo])
    #pyplt.savefig(img, format = 'png')
    #img.seek(0)

    #plot_url = base64.b64encode(img.getvalue()).decode()

    return plotConPlugins(fig)

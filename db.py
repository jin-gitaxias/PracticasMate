##################################################################
#db.py
#Autor: Tomas Galvez
#Para: CEAB, UVG, Guatemala
#Creado en septiembre 2018
#Última modificación: 07/11/2018
#
#Módulo de funciones para conexión y manejo de una base de datos
#PostgreSQL con psycopg2 y configparser.
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

import psycopg2 as ppg
from configparser import ConfigParser
from testing import debugPrint
from os import getcwd

conn = None

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
    global conn
    cur = None
    try:
        params = config()

        with open(".Renviron", "w") as f:
            f.write("PGHOST=" + params["host"] + "\nPGUSER=" + params["user"] + "\nPGPASSWORD=" + params["password"] + "\nDBNAME=" + params["database"])
        f.close()
        #print(params)

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
        #return conn

#Realiza un query provisto en el parámetro q. Devuelve el resultado de la consulta o None.
def query(q):
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

#Obtiene los nombres y tipos de las columnas en la tabla especificada.
def getColumns(table):
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
def getTables():
    if conn is not None:
        cur = conn.cursor()
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        tablas = list(cur.fetchall())
        for t in range(len(tablas)):
            tablas[t] = tablas[t][0]
        cur.close()
        return tablas
        
#Convierte una fecha en formato YYYY/MM/DD a algo reconocible por PostgreSQL.
def castFecha(fecha):
    return '\'' + fecha + '\'::date'

#Metodo para exportación de resultados de un query a archivo csv. Inutilizado
#(se reemplazó por exportación de csv mediante Pandas).
def exportFile(query, filename = 'datosMeteorologicosUVG'):
    r = 0
    if conn is not None:
        f = open(getcwd() + '\\descargas\\' + filename + '.csv', 'w')
        s = 'COPY (' + query + ') TO STDOUT WITH CSV HEADER'
        debugPrint("El comando COPY resultante es: " + str(s))
        cur = conn.cursor()
        debugPrint("Ejecutando COPY")
        r = cur.copy_expert(s, f)
        cur.close()
        f.close()
    return(r)

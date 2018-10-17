##################################################################
#pruebaGraficas.py
#Autor: Tomas Galvez
#Para: CEAB, UVG, Guatemala
#Creado en agosto 2018
#Última modificación: 24/08/2018
#
#Programa para pruebas de funciones en módulo graficas.py.
##################################################################

from graficas import *
import os

print(os.getcwd())

campoy = 'Temp.Out'

conn = connect()

try:
    qDia = armarQuery('X..Date', campoy, '2014-2018SanJacinto')
    rDia = query(conn, qDia)

    if rDia is not None:
        dfD = rowsToDataFrame(campoy, rDia)
        plotPorHora(dfD, campoy)
        plotPorDia(dfD, campoy)

    qMes = armarQuery('Mes', campoy, '2014-2018SanJacinto')
    rMes = query(conn, qMes)

    if rMes is not None:
        dfM = rowsToDataFrame(campoy, rMes, 'Mes')
        plotPorMes(dfM, campoy)

except (Exception) as e:
    print('Ocurrio un error')
    print(e)

finally:
    if (conn is not None):
        conn.close()

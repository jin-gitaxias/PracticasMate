##################################################################
#pruebaGraficas.py
#Autor: Tomas Galvez
#Para: CEAB, UVG, Guatemala
#Creado en agosto 2018
#Última modificación: 29/10/2018
#
#Programa para pruebas de funciones en módulo graficas.py.
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

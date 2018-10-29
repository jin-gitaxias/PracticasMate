##################################################################
#SQLqueries.py (nombre temporal)
#Autor: Tomas Galvez
#Para: CEAB, UVG, Guatemala
#Creado en septiembre 2018
#Última modificación: 29/10/2018
#
#Módulo de funciones para armar queries SQL independientes (lo más
#posible) del DBMS.
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

#Para centralizar el nombre del campo de fecha y hora.
def getDatetimeField():
    r = "Datetime"
    return r

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
        s1 += '"' + getDateField() + '" >= ' + fechai 
        if (fechaf is not None):
            s1 += " AND "

    if (fechaf is not None):
        s2 += '"' + getDateField() + '" <= ' + fechaf   
    
    return  s1 + s2

#Función para armar queries de dos campos. Su propósito es obtener los ejes para una gráfica univariable.
def armarQuery(tabla, campox, campoy = None, where = None):
    if (campox == "datetimefield"):
        campox = getDatetimeField()
    elif (campox == "datefield"):
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

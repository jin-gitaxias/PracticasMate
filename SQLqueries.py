##################################################################
#SQLqueries.py (nombre temporal)
#Autor: Tomas Galvez
#Para: CEAB, UVG, Guatemala
#Creado en septiembre 2018
#Última modificación: 12/09/2018
#
#Módulo de funciones para armar queries SQL independientes (lo más
#posible) del DBMS.
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

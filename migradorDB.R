##################################################################
#migradorDB.R
#Autor: Tomas Galvez
#Para: CEAB, UVG, Guatemala
#Creado en junio 2018
#Ultima modificacion: 29/10/2018
#
#Script para migración a una base de datos de los datos exportados
#en archivos de texto por estaciones meteorologicas del CEAB.
#El manejador de base de datos destino es PostgresSQL y los datos
#de nombre y de autenticación se encuentran en el código (y en
#'database.ini').
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

library(RPostgres)
library(chron)
library(utils)

debug_print <- function(log){
  print(log)
}

conectar <- function() {
  dbname <- ""
  user <- ""
  password <- ""#scan("pgpass", what="")
  #host <- ""
  con <- dbConnect(RPostgres::Postgres(), user=user, dbname=dbname)
  
  print(summary(con))
  
  con 
}

insert <- function(vec, posiciones, reemplazos){
  for (p in length(posiciones):1){
    vec <- append(vec, reemplazos[[p]], after = posiciones[[p]])
    #print(vec)
  }
  
  vec
}

ajustarEncabezados <- function(primeraLinea, segundaLinea){
  
  primeraLinea[[30]] <- "InAir"
  primeraLinea <- primeraLinea[!primeraLinea == "Air"]
  primeraLinea <- primeraLinea[!primeraLinea == "Arc."]
  
  primeraLinea <- insert(primeraLinea, c(0, 0, 14, 14, 30), c("-", "-", "-", "-", "-"))
  debug_print(primeraLinea)
  
  return (paste(primeraLinea, segundaLinea))
}

armarDf <- function(ubicacion, archivoDeDatos){
  #----Obtencion y curacion de datos----
  
  locale_original_LC_TIME <- Sys.getlocale("LC_TIME") 
  Sys.setlocale("LC_TIME", "C") #Modificar locale para reconocimiento de horas (el original se almacena en locale_original y se reestablece al final del script)
  
  #Importacion y formato de datos
  setwd(ubicacion) #"C:/Users/djincer/Desktop/estacionesMeto"
  ubicacionYArchivo <- c(getwd(), paste("/", archivoDeDatos, sep="")) #backup2014to2018abril30_sanjacinto.txt
  archivo <- paste(ubicacionYArchivo, collapse="")
  debug_print(archivo)
  header1 <- scan(archivo, nlines=1, what=character())
  debug_print(header1)
  header2 <- scan(archivo, nlines=1, skip=1, what=character())
  debug_print(header2)
  #header <- paste(header1, header2)
  header <- ajustarEncabezados(header1, header2)
  #debug_print(paste("***", header, "***"))
  tidy_header <- make.names(header, unique = TRUE) #Hacer nombres de columnas mas faciles de referenciar
  debug_print(tidy_header)
  
  #datos es el data frame con los datos originales
  datos <- read.table(archivo, sep="\t", fill=TRUE, skip=2, row.names = NULL)
  names(datos) <- tidy_header
  debug_print("read.table exitoso")
  debug_print(str(datos))
  debug_print(datos$X..Time)
  
  #Se modifican los indicadores de AM/PM en las horas para el reconocimiento de acuerdo al locale elegido (C)
  datos$X..Time <- gsub("a", "am", datos$X..Time)
  datos$X..Time <- gsub("p", "pm", datos$X..Time)
  debug_print("gsubs ejecutados")
  
  #Se agrega una columna que combina la informacion de fecha y hora en un unico campo de tipo datetime
  datos$Datetime <- as.POSIXct(paste(datos$X..Date, datos$X..Time), format="%d/%m/%y %I:%M %p") #Se combinan y convierten fecha y hora en una columna nueva
  debug_print("Columna Datetime creada exitosamente")
  
  Sys.setlocale("LC_TIME", locale_original_LC_TIME)
  
  
  columnas_a_convertir <- c("Temp.Out", "Hi.Temp", "Low.Temp", 
                            "Out.Hum", "Dew.Pt.", "Wind.Speed",
                            "Wind.Run", "Hi.Speed", "Wind.Chill",
                            "Heat.Index", "THW.Index", "THSW.Index",
                            "X..Bar", "X..Rain", "Rain.Rate",
                            "Solar.Rad.","Solar.Energy","Hi.Rad.",
                            "Hi.D.D","Heat.D.D", "Cool.Temp",
                            "In.Hum", "In.Dew", "In.Heat",
                            "In.EMC", "In.Density", "InAir.ET",
                            "X..Samp", "Wind.Tx", "Wind.Recept", "ISS.Int.")
  
  #Conversion de columnas numericas (son importadas como tipo factor)
  for (columna in columnas_a_convertir){
    datos[[columna]]<-as.numeric(as.character(datos[[columna]]))
  }
  
  datos[["X..Date"]] <- as.Date(as.POSIXct(datos[["X..Date"]], format="%d/%m/%y")) #Conversion de columna de fecha a tipo datetime (para agrupacion y resumen por dia)
  datos$Mes <- format(datos$X..Date, "%m/%y")
  datos[["Mes"]] <- as.Date(as.POSIXct(paste("01/", datos[["Mes"]]), format="%d/%m/%y"))
  debug_print("Columna Mes creada exitosamente")
  
  return(datos)
}

out <- tryCatch(
  {
    d <- as.data.frame(armarDf("C:/Users/djincer/Desktop/estacionesMeto", "SanJacintoJulio_12_09_2018.txt"))
    dbc <- conectar()
    dbWriteTable(dbc, name="2014-2018SanJacinto", value=d, row.names=FALSE, overwrite=TRUE)
  },
  error=function(cond){
    message("Claveles")
    message(cond)
    return(NA)
  }, finally={
    print("Desde el finally")
    dbDisconnect(dbc)
  }
)
print(out)

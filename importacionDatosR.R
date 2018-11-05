##################################################################
#importacionDatosR.R
#Autor: Tomas Galvez
#Para: CEAB, UVG, Guatemala
#Creado en junio 2018
#Ultima modificacion: 29/10/2018
#
#Script para importacion y graficado de datos exportados
#en archivos de texto por estaciones meteorologicas del CEAB.
#El proposito es disponer de graficas para analisis exploratorio.
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
library(ggplot2)
library(plyr)
library(dplyr)
library(forecast)
library(tseries)
library(lubridate)

#----Obtencion y curacion de datos----

locale_original_LC_TIME <- Sys.getlocale("LC_TIME") 
Sys.setlocale("LC_TIME", "C") #Modificar locale para reconocimiento de horas (el original se almacena en locale_original y se reestablece al final del script)

#Importacion y formato de datos
setwd("C:/Users/djincer/Desktop")
ubicacionYArchivo <- c(getwd(),"/backup2014to2018abril30_sanjacinto.txt")
archivo <- paste(ubicacionYArchivo, collapse="")
header1 <- scan(archivo, nlines=1, what=character())
header2 <- scan(archivo, nlines=1, skip=1, what=character())
header <- paste(header1, header2)
tidy_header <- make.names(header, unique = TRUE) #Hacer nombres de columnas mas faciles de referenciar

#datos es el data frame con los datos originales
datos <- read.table(archivo, sep="\t", fill=TRUE, skip=2, row.names = NULL)
names(datos) <- tidy_header

#Se modifican los indicadores de AM/PM en las horas para el reconocimiento de acuerdo al locale elegido (C)
datos$X..Time <- gsub("a", "am", datos$X..Time)
datos$X..Time <- gsub("p", "pm", datos$X..Time)
#Se agrega una columna que combina la informacion de fecha y hora en un unico campo de tipo datetime
datos$Datetime <- as.POSIXct(paste(datos$X..Date, datos$X..Time), format="%d/%m/%Y %I:%M %p") #Se combinan y convierten fecha y hora en una columna nueva

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

datos[["X..Date"]] <- as.POSIXct(datos[["X..Date"]], format="%d/%m/%Y") #Conversion de columna de fecha a tipo datetime (para agrupacion y resumen por dia)
datos$Mes <- format(datos$X..Date, "%y %m")

#datos_agrupados es el data frame con los grupos asignados (pero los datos intactos)
datos_agrupados_por_dia <- group_by(datos, X..Date) #Agrupacion de datos por dia
datos_agrupados_por_mes <- group_by(datos, Mes) #Agrupacion de datos por mes

#datos_resumidos_por_dia contiene los datos numericos resumidos en promedio por dia
datos_resumidos_por_dia <- dplyr::summarize(datos_agrupados_por_dia, 
                                    Temp.Out=mean(Temp.Out), 
                                    Hi.Temp=mean(Hi.Temp),
                                    Low.Temp=mean(Low.Temp),
                                    Out.Hum=mean(Out.Hum),
                                    In.Hum=mean(In.Hum),
                                    Dew.Pt.=mean(Dew.Pt.),
                                    In.Dew=mean(In.Dew),
                                    Wind.Speed=mean(Wind.Speed),
                                    Wind.Run=mean(Wind.Run),
                                    Hi.Speed=mean(Hi.Speed),
                                    Wind.Chill=mean(Wind.Chill),
                                    Heat.Index=mean(Heat.Index),
                                    THW.Index=mean(THW.Index),
                                    THSW.Index=mean(THSW.Index),
                                    X..Bar=mean(X..Bar),
                                    X..Rain=mean(X..Rain),
                                    Rain.Rate=mean(Rain.Rate),
                                    Solar.Rad.=mean(Solar.Rad.),
                                    Solar.Energy=mean(Solar.Energy),
                                    Hi.Rad.=mean(Hi.Rad.),
                                    Hi.D.D=mean(Hi.D.D),
                                    Heat.D.D=mean(Heat.D.D),
                                    Cool.Temp=mean(Cool.Temp),
                                    In.Heat=mean(In.Heat),
                                    In.EMC=mean(In.EMC),
                                    In.Density=mean(In.Density),
                                    InAir.ET=mean(InAir.ET),
                                    X..Samp=mean(X..Samp),
                                    Wind.Tx=mean(Wind.Tx),
                                    Wind.Recept=mean(Wind.Recept),
                                    ISS.Int.=mean(ISS.Int.))
#--------

#datos_resumidos_por_dia contiene los datos numericos resumidos en promedio por mes
datos_resumidos_por_mes <- dplyr::summarize(datos_agrupados_por_mes, 
                                            Temp.Out=mean(Temp.Out), 
                                            Hi.Temp=mean(Hi.Temp),
                                            Low.Temp=mean(Low.Temp),
                                            Out.Hum=mean(Out.Hum),
                                            In.Hum=mean(In.Hum),
                                            Dew.Pt.=mean(Dew.Pt.),
                                            In.Dew=mean(In.Dew),
                                            Wind.Speed=mean(Wind.Speed),
                                            Wind.Run=mean(Wind.Run),
                                            Hi.Speed=mean(Hi.Speed),
                                            Wind.Chill=mean(Wind.Chill),
                                            Heat.Index=mean(Heat.Index),
                                            THW.Index=mean(THW.Index),
                                            THSW.Index=mean(THSW.Index),
                                            X..Bar=mean(X..Bar),
                                            X..Rain=mean(X..Rain),
                                            Rain.Rate=mean(Rain.Rate),
                                            Solar.Rad.=mean(Solar.Rad.),
                                            Solar.Energy=mean(Solar.Energy),
                                            Hi.Rad.=mean(Hi.Rad.),
                                            Hi.D.D=mean(Hi.D.D),
                                            Heat.D.D=mean(Heat.D.D),
                                            Cool.Temp=mean(Cool.Temp),
                                            In.Heat=mean(In.Heat),
                                            In.EMC=mean(In.EMC),
                                            In.Density=mean(In.Density),
                                            InAir.ET=mean(InAir.ET),
                                            X..Samp=mean(X..Samp),
                                            Wind.Tx=mean(Wind.Tx),
                                            Wind.Recept=mean(Wind.Recept),
                                            ISS.Int.=mean(ISS.Int.))
#--------

#----Graficas univariable para cada campo (se hace cada grafica por separado para poder ejecutar las instrucciones individualmente)----

#Funciones para facilitar la graficada. Las funciones por hora y por dia estan hardcodeadas para trabajar con sus dataframes correspondientes
#getyrange obtiene el rango de valores en y de una grafica existente
getyrange <- function(ggplobj) ggplot_build(ggplobj)$layout$panel_ranges[[1]]$y.range

#plotporhora hace la grafica por hora sobre el data frame datos con x=Datetime. Toma como parametro el campo del df datos que se desea graficar
#y el titulo deseado de la grafica
plotporhora <- function(campo, titulo=NULL) {
  g <- ggplot(datos, aes(x=datos$Datetime, y=datos[[campo]])) + geom_point() + labs(x = "Horas", y = as.character(paste(campo, " por hora")))
  
  #Si se especifica un titulo, agregarlo
  if (!is.null(titulo)){
    g <- g + labs(title = titulo)
  }
  
  g
}

#plotpordia hace la grafica por dia sobre el data frame datos_resumidos_por_dia con x=X..Date. Toma como parametro el campo del df datos_resumidos_por_dia que se desea graficar,
#la grafica (existente) por hora para extraer y aplicar el mismo rango de valores "y" a la grafica por dia; y el titulo deseado de la grafica
plotpordia <- function(campo, objporhora=NULL, titulo=NULL) {
  g <- ggplot(datos_resumidos_por_dia, aes(x=datos_resumidos_por_dia$X..Date, y=datos_resumidos_por_dia[[campo]])) + geom_point() + labs(x = "Dias", y = as.character(paste(campo, " por dia")))
  
  #Si se especifica una grafica por hora existente se aplica la misma escala sobre el eje y
  if (!is.null(objporhora)){
    yrange <- getyrange(objporhora)
    g <- g + ylim(yrange)
  }
  
  #Si se especifica un titulo, agregarlo
  if (!is.null(titulo)){
    g <- g + labs(title = titulo)
  }
  g
}

#plotpormes hace la grafica por dia sobre el data frame datos_resumidos_por_mes con x=Mes. Toma como parametro el campo del df datos_resumidos_por_mes que se desea graficar,
#la grafica (existente) por hora para extraer y aplicar el mismo rango de valores "y" a la grafica por mes; y el titulo deseado de la grafica
plotpormes <- function(campo, objporhora=NULL, titulo=NULL) {
  g <- ggplot(datos_resumidos_por_mes, aes(x=datos_resumidos_por_mes$Mes, y=datos_resumidos_por_mes[[campo]])) + geom_point() + labs(x = "Meses", y = as.character(paste(campo, " por mes")))
  
  #Si se especifica una grafica por hora existente se aplica la misma escala sobre el eje y
  if (!is.null(objporhora)){
    yrange <- getyrange(objporhora)
    g <- g + ylim(yrange)
  }
  
  #Si se especifica un titulo, agregarlo
  if (!is.null(titulo)){
    g <- g + labs(title = titulo)
  }
  g
}

#diferenciacion provee el resultado de las diferencias consecutivas sobre un conjunto de valores. El parametro de orden especifica cuantas veces debe aplicarse
#la diferenciacion sobre el conjunto de datos provisto (e.g., si orden=2, se aplica diferenciacion a la diferenciacion del conjunto original de datos).
#El orden de diferenciacion debe ser tal que el conjunto de datos resultante tenga la menor desviacion estandar posible. Obtener la diferenciacion permitira
#hacer una serie de tiempo "mas estacionaria", para fines de aplicacion de obtencion modelo ARIMA.
diferenciacion <- function(datos, orden=1){
  datosCopia <- datos
  diferenciacionesRealizadas = 0
  
  #Ciclo que aplica diferenciacion sobre si misma "orden" veces
  while (diferenciacionesRealizadas < orden){
    tamano <- length(datosCopia)# - 1
    diferencias <- numeric(tamano)
    #for (i in seq(0, tamano - 1)){
    for (i in seq(0, tamano)){
      diferencias[i] <- datosCopia[i + 1] - datosCopia[i]
    }
    datosCopia <- diferencias
    diferenciacionesRealizadas <- diferenciacionesRealizadas + 1
  }
  
  datosCopia
}

diferenciacionPorTemporada <- function(datos, seasonality, orden=1){
  datosCopia <- datos
  diferenciacionesRealizadas = 0
  
  #Ciclo que aplica diferenciacion con un lag igual a la temporada especificada en "seasonality".
  #La diferenciacion se aplica sobre si misma "orden" veces.
  while (diferenciacionesRealizadas < orden){
    tamano <- length(datosCopia)# - seasonality
    diferencias <- numeric(tamano)
    #for (i in seq(0, tamano - 1)){
    for (i in seq(0, tamano)){
      diferencias[i] <- datosCopia[i + seasonality] - datosCopia[i]
    }
    datosCopia <- diferencias
    diferenciacionesRealizadas <- diferenciacionesRealizadas + 1
  }
  
  datosCopia
}

#Temperatura por hora
g1 <- plotporhora("Temp.Out", "Temperatura externa por hora")
g1
g2 <- plotporhora("Hi.Temp", "Temperatura externa maxima por hora")
g2
g3 <- plotporhora("Low.Temp", "Temperatura externa minima por hora")
g3

#Temperatura por dia
plotpordia("Temp.Out", g1, "Temperatura externa por dia")
plotpordia("Hi.Temp", g2, "Temperatura externa maxima por dia")
plotpordia("Low.Temp", g3, "Temperatura externa minima por dia")

plotpormes("Temp.Out", g1, "Temperatura externa por mes")

#Graficas de autocorrelacion sobre los datos de Temp.Out originales y los una vez diferenciados.
lagMax <- 1200 #Ajustar el lag de ACF segun sea necesario
temperaturasExternasPorMes <- datos_resumidos_por_mes$Temp.Out
diferencias <- diferenciacion(temperaturasExternasPorMes)
diferencias2 <- diferenciacionPorTemporada(temperaturasExternasPorMes, 12)
#decomp <- stl(tsclean(ts(diferencias, frequency=7)), s.window="periodic")
#deseas <- seasadj(decomp)

ggAcf(temperaturasExternasPorMes, lag.max = lagMax)
ggPacf(temperaturasExternasPorMes, lag.max = lagMax)
tsOriginales <- ts(temperaturasExternasPorMes, frequency = 12)
#ggAcf(diferencias, lag.max = lagMax) #Segun entiendo, adf.test confirma que la serie de diferencias es en efecto lo mas estacionario que puedo buscar
#ggPacf(diferencias, lag.max = lagMax)
ggAcf(diferencias2, lag.max = lagMax)
ggPacf(diferencias2, lag.max = lagMax)
tsDiferencias2 <- ts(diferencias2, frequency=12)

#Todo a continuacion hay que rehacerlo con las nuevas funciones

#Humedad por hora
ggplot(datos, aes(x=datos$Datetime, y=datos$Out.Hum)) + geom_point()
ggplot(datos, aes(x=datos$Datetime, y=datos$In.Hum)) + geom_point()

#Humedad por dia
ggplot(datos_resumidos, aes(x=datos_resumidos$X..Date, y=datos_resumidos$Out.Hum)) + geom_point()
ggplot(datos_resumidos, aes(x=datos_resumidos$X..Date, y=datos_resumidos$In.Hum)) + geom_point()

#Punto de rocio por hora
ggplot(datos, aes(x=datos$Datetime, y=datos$Dew.Pt.)) + geom_point()
ggplot(datos, aes(x=datos$Datetime, y=datos$In.Dew)) + geom_point()

#Punto de rocio por dia
ggplot(datos_resumidos, aes(x=datos_resumidos$X..Date, y=datos_resumidos$Dew.Pt.)) + geom_point()
ggplot(datos_resumidos, aes(x=datos_resumidos$X..Date, y=datos_resumidos$In.Dew)) + geom_point()

#velocidad del viento por hora
ggplot(datos, aes(x=datos$Datetime, y=datos$Wind.Speed)) + geom_point()
ggplot(datos, aes(x=datos$Datetime, y=datos$Hi.Speed)) + geom_point()

#Velocidad del viento por dia
ggplot(datos_resumidos, aes(x=datos_resumidos$X..Date, y=datos_resumidos$Wind.Speed)) + geom_point()
ggplot(datos_resumidos, aes(x=datos_resumidos$X..Date, y=datos_resumidos$Hi.Speed)) + geom_point()

#Wind Run por hora
ggplot(datos, aes(x=datos$Datetime, y=datos$Wind.Run)) + geom_point()

#Wind Run por dia
ggplot(datos_resumidos, aes(x=datos_resumidos$X..Date, y=datos_resumidos$Wind.Run)) + geom_point()

#Sensacion termica del viento por hora
ggplot(datos, aes(x=datos$Datetime, y=datos$Wind.Chill)) + geom_point()

#Sensacion termica del viento por dia
ggplot(datos_resumidos, aes(x=datos_resumidos$X..Date, y=datos_resumidos$Wind.Chill)) + geom_point()

#Indices de calor por hora
ggplot(datos, aes(x=datos$Datetime, y=datos$Heat.Index)) + geom_point()
ggplot(datos, aes(x=datos$Datetime, y=datos$In.Heat)) + geom_point()

#Indices de calor por dia
ggplot(datos_resumidos, aes(x=datos_resumidos$X..Date, y=datos_resumidos$Heat.Index)) + geom_point()
ggplot(datos_resumidos, aes(x=datos_resumidos$X..Date, y=datos_resumidos$In.Heat)) + geom_point()

#THW y THSW por hora
ggplot(datos, aes(x=datos$Datetime, y=datos$THW.Index)) + geom_point()
ggplot(datos, aes(x=datos$Datetime, y=datos$THSW.Index)) + geom_point()

#THW y THSW por dia
ggplot(datos_resumidos, aes(x=datos_resumidos$X..Date, y=datos_resumidos$THW.Index)) + geom_point()
ggplot(datos_resumidos, aes(x=datos_resumidos$X..Date, y=datos_resumidos$THSW.Index)) + geom_point()

#Presion por hora
ggplot(datos, aes(x=datos$Datetime, y=datos$X..Bar)) + geom_point()

#Presion por dia
ggplot(datos_resumidos, aes(x=datos_resumidos$X..Date, y=datos_resumidos$X..Bar)) + geom_point()

#Estas faltan
#Degree days por hora
ggplot(datos)
qplot(datos$`- Date`, datos$`Hi D-D`)
qplot(datos$`- Date`, datos$`Heat D-D`)
qplot(datos$`- Date`, datos$`Cool Temp`)

#Lluvia
qplot(datos$`- Date`, datos$`- Rain`)
qplot(datos$`- Date`, datos$`Rain Rate`)

#Radiacion y energia solar
qplot(datos$`- Date`, datos$`Solar Rad.`)
qplot(datos$`- Date`, datos$`Solar Energy`)
qplot(datos$`- Date`, datos$`Hi Rad.`)

#Internas
#Humedad
qplot(datos$`- Date`, datos$`In Hum`)

#Punto de rocio
qplot(datos$`- Date`, datos$`In Dew`)
qplot(datos$`- Date`, datos$`In Heat`)
qplot(datos$`- Date`, datos$`In EMC`)
qplot(datos$`- Date`, datos$`In Density`)
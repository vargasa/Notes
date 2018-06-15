# -*- coding: utf-8 -*-
"""
# Analyzing Elections Results
"""
# python3
# For easy use paste code into https://colab.research.google.com/
# http://k-lab.tk/content/html/elections201801.php
import requests # handle http request
import json # parse JSON responses from website
import matplotlib.pyplot as plt # canvas and plots
import matplotlib as mpl # ticker
import pandas as pd # Mainly DataFrames
import math
!pip install -q shapely
from shapely.geometry.polygon import Polygon  # In order to draw Maps
from shapely import affinity # Geometric transformations
!pip install -q descartes
from descartes import PolygonPatch # AreaFilled Polygons

# In order to keep the use of the Elections API as low as possible
# We will use Google Drive to save the downloaded responses and
# use them if available in Drive
# https://colab.research.google.com/notebooks/io.ipynb#scrollTo=zU5b6dlRwUQk

!pip install -U -q PyDrive
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from google.colab import auth
from oauth2client.client import GoogleCredentials
import io
from googleapiclient.http import MediaIoBaseDownload

# 1. Authenticate and create the PyDrive client.
auth.authenticate_user()
gauth = GoogleAuth()
gauth.credentials = GoogleCredentials.get_application_default()
drive = GoogleDrive(gauth)

"""The following is a hard coded list of codes for each state.  CDP is an internal code used to identify each state info, while DPTO_CCDGO is used in order to identify the geometry of each state. I'm trying to keep consistent de notation along the notebook."""

# hardcoded dptos codes
dptos = '[{ "CDP": "01" , "DPTO_CCDGO": "05" , "name":" Antioquia " },{ "CDP": "03" , "DPTO_CCDGO": "08" , "name":" Atlántico " },{ "CDP": "05" , "DPTO_CCDGO": "13" , "name":" Bolívar " },{ "CDP": "07" , "DPTO_CCDGO": "15" , "name":" Boyacá " },{ "CDP": "09" , "DPTO_CCDGO": "17" , "name":" Caldas " },{ "CDP": "11" , "DPTO_CCDGO": "19" , "name":" Cauca " },{ "CDP": "12" , "DPTO_CCDGO": "20" , "name":" Cesar " },{ "CDP": "13" , "DPTO_CCDGO": "23" , "name":" Córdoba " },{ "CDP": "15" , "DPTO_CCDGO": "25" , "name":" Cundinamarca " },{ "CDP": "16" , "DPTO_CCDGO": "11" , "name":" Bogotá D.C  " },{ "CDP": "17" , "DPTO_CCDGO": "27" , "name":" Chocó " },{ "CDP": "19" , "DPTO_CCDGO": "41" , "name":" Huila " },{ "CDP": "21" , "DPTO_CCDGO": "47" , "name":" Magdalena " },{ "CDP": "23" , "DPTO_CCDGO": "52" , "name":" Nariño " },{ "CDP": "24" , "DPTO_CCDGO": "66" , "name":" Risaralda " },{ "CDP": "25" , "DPTO_CCDGO": "54" , "name":" Norte de Santander " },{ "CDP": "26" , "DPTO_CCDGO": "63" , "name":" Quindío " },{ "CDP": "27" , "DPTO_CCDGO": "68" , "name":" Santander " },{ "CDP": "28" , "DPTO_CCDGO": "70" , "name":" Sucre " },{ "CDP": "29" , "DPTO_CCDGO": "73" , "name":" Tolima " },{ "CDP": "31" , "DPTO_CCDGO": "76" , "name":" Valle del Cauca " },{ "CDP": "40" , "DPTO_CCDGO": "81" , "name":" Arauca " },{ "CDP": "44" , "DPTO_CCDGO": "18" , "name":" Caquetá " },{ "CDP": "46" , "DPTO_CCDGO": "85" , "name":" Casanare " },{ "CDP": "48" , "DPTO_CCDGO": "44" , "name":" La Guajira " },{ "CDP": "50" , "DPTO_CCDGO": "94" , "name":" Guainía " },{ "CDP": "52" , "DPTO_CCDGO": "50" , "name":" Meta " },{ "CDP": "54" , "DPTO_CCDGO": "95" , "name":" Guaviare " },{ "CDP": "56" , "DPTO_CCDGO": "88" , "name":" San Andrés y Providencia " },{ "CDP": "60" , "DPTO_CCDGO": "91" , "name":" Amazonas " },{ "CDP": "64" , "DPTO_CCDGO": "86" , "name":" Putumayo " },{ "CDP": "68" , "DPTO_CCDGO": "97" , "name":" Vaupés " },{ "CDP": "72" , "DPTO_CCDGO": "99" , "name":" Vichada " },{ "CDP": "88" , "DPTO_CCDGO": "", "name":" Consulados " }]'
dptos = json.loads(dptos);

dptoCodes = [dptos[i]["CDP"] for i in range(len(dptos))]

# Allow us to get the name of the state based on its CDP

def getDpto(cdp) :
  cdp = str(cdp).zfill(2)
  for i in range(len(dptos)) :
    if(dptos[i]["CDP"] == cdp) : return dptos[i]["name"]

# We also define a pd:DataFrame containing this labels:

table = []
for i in dptos :
  reg = []
  reg.append(i['CDP'])
  reg.append(i['DPTO_CCDGO'])
  reg.append(i['name'])
  table.append(reg)  
  
dfDpto = pd.DataFrame(table)
dfDpto.columns = ['CDP','DPTO_CCDGO','name']

# Please note that this is temporal as dfDpto is redefined later to include more information

"""In the following section, we get the data directly from the JSON "API". Some hardcoded values have its own interpretation:

```
NEN	: numBoletin
HMS	: mmddhhmm - date
MTO	: mesTotales
MES	: mesEscrutadas
PME	: porcMesEscrutadas
CEN	: censo
TNM	: votosNoMarc
PTN	: porcVotNoMarc
VOT	: votantes
PVO	: porcVotantes
ABS	: abstencion
PAB	: porcAbstencion
VBL	: votosBlancos
PVB	: porcVotBlancos
VVA	: votosValidos
PVV	: porcVotosValidos
VNU	: votosNulos
PVN	: porcVotosNulos
VCA	: votosCandid
PVC	: porcVotosCandid

```
"""

# Get the file and keep it in Google Drive for future use
# returns the content in a string

def getFile(url,filename) :

  stringContent = "";

  fls = drive.ListFile({'q': "title='"+filename+"' "}).GetList()

  if (len(fls) == 0) : # Not in drive
    print("Retrieving",filename, " from: ", url)
    stringContent = requests.get(url+filename, stream=True) 
    stringContent.encoding = 'iso-latin-1'
    stringContent = stringContent.text
    fileOutput = drive.CreateFile({ 'title' : filename })
    fileOutput.SetContentString(stringContent)
    fileOutput.Upload()
    print('Uploaded file:',filename,fileOutput.get('id'))
  else :
    stringContent = drive.CreateFile({ 'id' : fls[0]['id'] }) # taking the very first result
    stringContent = stringContent.GetContentString()
    print("Retrieving from Drive:", filename )
    
  return stringContent;

url = 'https://presidente2018.registraduria.gov.co/resultados/data/PR/'
filename = 'DZZZZZZZZZZZZZZZZZ.json'

# D+ZZ+ZZZ+ZZZZZZZZZZZZ.json Allow us to get access to the data
# the first ZZ indicates the CDP of the state while the second ZZZ
# stands for a code assigned to municipalities. The municipalities code
# belongs to each department and it is not unique at the federal level
# we will get a table relating State/Municipalities relation later
# the other ZZZZZZ string can belong to "Zona,Puesto" levels but none
# of them seems to be public.
# It doesn't look professional should be old mantained code
# ZZ itself is the national level.

# Table will contain Dpto data
table = [] 
dataKeys = ['NEN','HMS','MTO','MES','PME','CEN','TNM','PTN','VOT','PVO','ABS','PAB','VBL','PVB','VVA','PVV','VNU','PVN','VCA','PVC']
rawData = []

# Loop over all states and build a DataFrame
for i in range(len(dptos)):

    # JSON request
    filename = "D"+dptos[i]['CDP']+"ZZZZZZZZZZZZZZZ.json"
    datos = getFile(url,filename);
    datos = json.loads(datos)
    # Here we can check that information is in fact related by printing dptos vs datos info
    print("Downloading", dptos[i]['name'], "CDP: ", datos['generales']['ambito']['CDP']);
    
    # 1 row per CDP
    reg = []
    reg.append(dptos[i]['name'])
    reg.append(datos['generales']['ambito']['CDP'])
    reg.append(dptos[i]['DPTO_CCDGO'])

    
    for j in dataKeys :
      
      reg.append(int(datos['generales']['escrutinio'][j]))
    
    # 'candidatos' is a JSON string which containd valuable info
    # regarding results for the candidate in each state/municipiality
    reg.append(datos['candidatos'])
    
    table.append(reg)
    rawData.append(datos)
    
dataKeys.insert(0,'dptoName')
dataKeys.insert(1,'CDP')
dataKeys.insert(2,'DPTO_CCDGO')
dataKeys.append("candidatos")

dfDpto = pd.DataFrame(table)
dfDpto.columns = dataKeys

dfDpto 
# from here we can use df DataFrame to Query DPTO Info

# Each candidate has being assigned a code "CCA" and a color
for i in dfDpto["candidatos"][0] :
  print(i["NC1"],i["CCA"],i["COL"])

"""Once the data has been downloaded you can start playing with it:"""

# Size of the initial plots
fs=(8,8) # figuresize
w=0.9 # width

#print(plt.style.available)
plt.style.use('seaborn-colorblind')
dfDpto = dfDpto.sort_values(by='CEN', ascending=False)
ax = dfDpto.plot.bar(x="dptoName",y="CEN",width=w,figsize=fs)
# https://stackoverflow.com/questions/25973581/how-do-i-format-axis-number-format-to-thousands-with-a-comma-in-matplotlib
ax.yaxis.set_major_formatter(mpl.ticker.StrMethodFormatter('{x:,.0f}'))
# https://stackoverflow.com/questions/12608788/changing-the-tick-frequency-on-x-or-y-axis-in-matplotlib
ax.yaxis.set_major_locator(mpl.ticker.MultipleLocator(5e5))
subtitulo = '\nElecciones Presidenciales 2018\nPrimera Vuelta'
plt.title("Censo Electoral por Departamentos"+subtitulo)
plt.xlabel('Departamentos')
plt.ylabel('Número de personas habilitadas para votar')
plt.show()

# Bokeh provides a way to create interactive plots (Enabled by JS)
!pip install -q bokeh

from bokeh.io import show, output_file, push_notebook, output_notebook
from bokeh.models import ColumnDataSource, HoverTool, NumeralTickFormatter
from bokeh.palettes import cividis
from bokeh.plotting import figure
from random import shuffle

output_notebook () # You have can use output_file() as well

xx = list(dfDpto.dptoName)
yy = list(dfDpto.CEN)

colorList = cividis(len(xx))
shuffle(colorList)

source = ColumnDataSource(
    data = dict(xdata = xx , ydata=yy, color=colorList)
)

tools = "pan,wheel_zoom,box_zoom,reset,save".split(',')
hover = HoverTool(tooltips=[
    ("Dpto:", "@xdata"),
    ("Censo:", "@ydata")
    
])
tools.append(hover)

p = figure(
    x_range= xx,
    #y_range=(0,9),
    plot_height=600,
    plot_width=600,
    title="Censo Electoral por Departamentos"+subtitulo,
    #toolbar_location=None,
    tools=tools
)

p.vbar(
    x='xdata',
    top='ydata',
    width=0.9,
    color='color',
    #legend="xdata",
    source=source
)

p.yaxis.axis_label = "Número de personas habilitadas para votar"
p.xaxis.axis_label = "Departamentos"
p.xgrid.grid_line_color = None
p.xaxis.major_label_orientation = math.pi/2
p.legend.orientation = "horizontal"
p.legend.location = "top_center"
p.yaxis[0].formatter = NumeralTickFormatter(format="0,0")

show(p)

dfDpto = dfDpto.sort_values(by='ABS', ascending=False)
ax = dfDpto.plot.bar(x='dptoName',y='ABS',width=w,figsize=fs)
ax.yaxis.set_major_formatter(mpl.ticker.StrMethodFormatter('{x:,.0f}'))
# https://stackoverflow.com/questions/12608788/changing-the-tick-frequency-on-x-or-y-axis-in-matplotlib
ax.yaxis.set_major_locator(mpl.ticker.MultipleLocator(5e5))
plt.title("Abstención"+subtitulo)
plt.xlabel('Departamentos')
plt.ylabel('Número de personas que se abstuvieron de votar')
plt.show()

dfDpto = dfDpto.sort_values(by='ABS', ascending=False)

output_notebook ()

xx = list(dfDpto.dptoName)
yy = list(dfDpto.ABS)

colorList = cividis(len(xx))
shuffle(colorList)

source = ColumnDataSource(
    data = dict(xdata = xx , ydata=yy, color=colorList)
)

tools = "pan,wheel_zoom,box_zoom,reset,save".split(',')
hover = HoverTool(tooltips=[
    ("Dpto:", "@xdata"),
    ("Censo:", "@ydata")
    
])
tools.append(hover)

p = figure(
    x_range= xx,
    #y_range=(0,9),
    plot_height=500,
    plot_width=500,
    title="Abstención"+subtitulo,
    #toolbar_location=None,
    tools=tools
)

p.vbar(
    x='xdata',
    top='ydata',
    width=0.9,
    color='color',
    #legend="xdata",
    source=source
)

p.yaxis.axis_label = "Número de personas que se abstuvieron de votar"
p.xaxis.axis_label = "Departamentos"
p.xgrid.grid_line_color = None
p.xaxis.major_label_orientation = math.pi/2
p.legend.orientation = "horizontal"
p.legend.location = "top_center"
p.yaxis[0].formatter = NumeralTickFormatter(format="0,0")

show(p)

# do NOT mess up with the original data by doing this:
#dfDpto['PAB'] = dfDpto['PAB'] / 100
# At least no more than once

# PAB is associated with the percentage of people who didn't vote 
# (relative to each state in this case) 8000 == 80.00%

dfDpto = dfDpto.sort_values(by='PAB', ascending=False)
ax = dfDpto.plot.bar(x='dptoName',y='PAB',width=w,figsize=fs,color='r')

ax.yaxis.set_major_formatter(mpl.ticker.PercentFormatter())
plt.ylim(ymax=100)
plt.title('Abstención'+subtitulo)
plt.xlabel('Departamentos')
plt.ylabel('Nivel de abstención')
plt.show()

# do not mess up with the original data by doing this:
#dfDpto['PAB'] = dfDpto['PAB'] / 100

# PAB is associated with the percentage of people who didn't vote 
# (relative to each state in this case) 8000 == 80.00%

output_notebook ()

xx = list(dfDpto.dptoName)
yy = list(dfDpto.PAB)

colorList = cividis(len(xx))
shuffle(colorList)

source = ColumnDataSource(
    data = dict(xdata = xx , ydata=yy, color=colorList)
)

tools = "pan,wheel_zoom,box_zoom,reset,save".split(',')
hover = HoverTool(tooltips=[
    ("Dpto:", "@xdata"),
    ("Censo:", "@ydata")
    
])
tools.append(hover)

p = figure(
    x_range= xx,
    #y_range=(0,9),
    plot_height=500,
    plot_width=500,
    title='Nivel de abstención '+subtitulo,
    #toolbar_location=None,
    tools=tools
)

p.vbar(
    x='xdata',
    top='ydata',
    width=0.9,
    color='color',
    #legend="xdata",
    source=source
)

p.yaxis.axis_label = "Nivel de abstención"
p.xaxis.axis_label = "Departamentos"
p.xgrid.grid_line_color = None
p.xaxis.major_label_orientation = math.pi/2
p.legend.orientation = "horizontal"
p.legend.location = "top_center"
p.yaxis[0].formatter = NumeralTickFormatter(format="0,0%")

show(p)

# CEN represents the total number of people who is able to vote (in each state)
# VOT represents the total number of people who voted (in each state)
fs=(10,4) # figuresize
dfDpto = dfDpto.sort_values(by='CEN',ascending=False)
ax = dfDpto[["VOT","ABS"]].plot(kind='bar',width=w,figsize=fs, color=('g','r'),
                            stacked=False)
ax.set_xticklabels(dfDpto.dptoName)
ax.yaxis.set_major_formatter(mpl.ticker.StrMethodFormatter('{x:,.0f}'))
plt.title('Votantes y Abstencionistas por Departamentos'+subtitulo)
plt.xlabel('Departamentos')
plt.ylabel('# Votantes (VOT) \n # Abstencionistas(ABS)')
plt.show()

# Now, what I want is to compare the number of people who didn't vote vs 
# the candidate who got most of the votes in each state
# creates dfComparison (Comparison between abstencionism and candidate with most of the votes)
    
table = []
    
for i in range(len(rawData)) :
  reg = []
  reg.append(rawData[i]["generales"]["ambito"]["CDP"])
  reg.append(getDpto(rawData[i]["generales"]["ambito"]["CDP"]))
  
  # The very first element contains the candidate with more votes
  reg.append(rawData[i]["candidatos"][0]["CCA"]) 
  reg.append(rawData[i]["candidatos"][0]["NC1"])
  reg.append(int(rawData[i]["candidatos"][0]["PVF"]))
  reg.append(int(rawData[i]["candidatos"][0]["VFO"]))
  
  reg.append(int(rawData[i]['generales']['escrutinio']['ABS']))
  reg.append(int(rawData[i]['generales']['escrutinio']['PVO']))
  
  table.append(reg)
  
dfNalStat = pd.DataFrame(table)
dfNalStat.columns = ['CDP','dptoName','CCA','NC1','PVF','VFO','ABS','PVO']
dfNalStat = dfNalStat.sort_values(by='ABS',ascending=False)

ax = dfNalStat[['VFO','ABS']].plot(kind='bar', color=('g','r'), width=w, figsize = fs , stacked=False)
ax.set_xticklabels(dfNalStat.dptoName)

plt.title('Candidato con más alta votación vs abstencionistas'+subtitulo)
plt.xlabel('Departamentos')
plt.ylabel('Abstencionismo(Rojo) \n Candidato con mas alta votacion (Verde)')
plt.show()

# Note that ZZ.geojson contains info about the geometry of each state. ZZ in case of the federal level
url = "https://presidente2018.registraduria.gov.co/js/coords/"
filename = "ZZ.geojson"
mapData = getFile(url,filename)
mapData = json.loads(mapData)
#mapData['features'][0]['properties']['name']

#-------------------------------------------------------------
# Return the color code given the CCA (Code for each candidate)
def getColor(cca) :
  cca = int(cca)
  switcher = {
      3: '#54b8ec',
      6: '#A0BE00',
      1: '#8c00a0',
      8: '#0460a7',
      4: '#c0000d',
      2: '#919191',
      5: '#ffdc00',
      7: '#d58500'
  }
  return switcher.get(cca,"Invalid CCA")



def getCCAName(cca) :
  cca = int(cca)
  switcher = {
      3: 'Ivan Duque',
      6: 'Sergio Fajardo',
      1: 'Gustavo Petro',
      8: 'Vargas Lleras',
      4: 'De la Street',
      2: 'Promotores Voto en Blanco',
      5: 'Jorge Trujillo',
      7: 'Viviane Morales'
  }
  return switcher.get(cca,"Invalid CCA")
  


#-------------------------------------------------------------
# Draws a Map :D using shapely library (not Bokeh)
def drawMap(ax, points, 
            scaleFactor = 1, 
            facecolor = 'r', 
            edgecolor = 'BLACK',
            linewidth = 1,
            alpha = 0.5) :
  shape = Polygon(points)
  shape = affinity.scale(shape, 
                         xfact= scaleFactor, 
                         yfact=scaleFactor)
  x,y = shape.exterior.xy
  patch = PolygonPatch(shape, 
                       edgecolor = edgecolor,
                       facecolor = facecolor,
                       linewidth = linewidth, 
                       alpha=alpha)
  ax.add_patch(patch)
#-------------------------------------------------------------

#for i in range(len(mapData["features"])) : 

fig = plt.figure(1, figsize=(12,12), dpi=90)

ax = fig.add_subplot(111)

for i in range(32) : # 33 is a MultiPolygon for consulados coordinates[i][0]
  
  dptoCDP = dfDpto.loc[ 
      dfDpto['DPTO_CCDGO'] == mapData["features"][i]["properties"]['DPTO_CCDGO'] 
  ]['CDP'].iloc[0]
  
  cca = dfNalStat.loc[
      dfNalStat['CDP'] == dptoCDP
  ]['CCA'].iloc[0]
  
  # PVF: Percentage of votes for a given Candidate
  # in this case the winner in the state
  pvf = dfNalStat.loc[
      dfNalStat['CDP'] == dptoCDP
  ]['PVF'].iloc[0] * 1e-4  # to get something between [0,1]
  
  # PVO: Percentage of people in each state who voted
  dptoPVO = dfDpto.loc[
      dfDpto['CDP'] == dptoCDP
  ]['PVO'].iloc[0] * 1e-04
  
  # CEN
  dptoCENrel = dfDpto.loc[
      dfDpto['CDP'] == dptoCDP # 10 is just an amplitude factor
  ]['CEN'].iloc[0] *(10/36783940) # 36783940 means the national censo
  
  # VOT: Number of people who voted
  dptoVOT = dfDpto.loc[
      dfDpto['CDP'] == dptoCDP
  ]['VOT'].iloc[0] *(5/36783940)
  
  scaleFactor2 = pvf;

  print("Adding :", "CDP:", dptoCDP, mapData['features'][i]['properties']['name'],"CCA:", cca)
  
  coordinates = mapData["features"][i]["geometry"]["coordinates"][0]
  
  drawMap(ax,coordinates,facecolor='WHITE')
  ### scaleFactor = normalize(shapeDpto,1); # First do normalization then rescale
  # SCALED
  drawMap(ax,coordinates,scaleFactor2,facecolor=getColor(cca),edgecolor='WHITE')
  

# Need to fix islands and Embassies
for i in range(len(mapData["features"][32]["geometry"]["coordinates"])) : # San Andres y Providencia  
  dptoCDP = '56'
  
  cca = dfNalStat.loc[
      dfNalStat['CDP'] == dptoCDP
  ]['CCA'].iloc[0]
  
  dptoPVO = dfDpto.loc[
      dfDpto['CDP'] == dptoCDP
  ]['PVO'].iloc[0] * 1e-04

  geoPoints = mapData["features"][32]["geometry"]["coordinates"][i][0]
  drawMap(ax,geoPoints, facecolor='WHITE')
  drawMap(ax,geoPoints,scaleFactor =  dptoPVO, facecolor=getColor(cca))
  
  
for i in range(len(mapData["features"][33]["geometry"]["coordinates"])) : # Consulados
  
  dptoCDP = '88'
  
  cca = dfNalStat.loc[
      dfNalStat['CDP'] == dptoCDP
  ]['CCA'].iloc[0]
  
  dptoPVO = dfDpto.loc[
      dfDpto['CDP'] == dptoCDP
  ]['PVO'].iloc[0] * 1e-04
  
  drawMap(ax,mapData["features"][33]["geometry"]["coordinates"][i][0],facecolor='WHITE')
  drawMap(ax,mapData["features"][33]["geometry"]["coordinates"][i][0],scaleFactor = dptoPVO, facecolor=getColor(cca))
  
  
ax.set_xlim([-80,-60])
ax.set_ylim([-4,13])
ax.set_aspect(1)

from bokeh.io import show
from bokeh.models import (
    ColumnDataSource,
    HoverTool,
    LogColorMapper
)
from bokeh.plotting import figure
from bokeh.palettes import Viridis6 as palette

output_notebook ()

lons = []
lats = []
colors = []

for k in mapData["features"][0:-2]: # Take out islands and embassies
  
  dptoCDP = dfDpto.loc[ 
      dfDpto['DPTO_CCDGO'] == k["properties"]['DPTO_CCDGO'] 
  ]['CDP'].iloc[0]
  
  cca = dfNalStat.loc[
      dfNalStat['CDP'] == dptoCDP
  ]['CCA'].iloc[0]
  
  colors.append(getColor(cca))
  coords = k["geometry"]["coordinates"][0]
  lons.append([coords[i][0] for i in range(len(coords))])
  lats.append([coords[i][1] for i in range(len(coords))])
  

source = ColumnDataSource(data=dict(
    x=lons,
    y=lats,
    colors=colors,
))

TOOLS = "pan,wheel_zoom,reset,hover,save"

p = figure(
    title="Texas Unemployment, 2009", 
    tools=TOOLS,
    x_axis_location=None, 
    y_axis_location=None
)
p.grid.grid_line_color = None

p.patches('x', 'y', source=source,
          fill_color = 'colors',
          fill_alpha=0.7, line_color="white", line_width=0.5)

show(p)

# returns a list containing the codes for the municipalities and its name
# for each state
def getMuns(cdp) : 
  cdp = str(cdp).zfill(2)
  url = "https://presidente2018.registraduria.gov.co/resultados/data/mun/"
  filename = "m"+cdp+"ZZZZZZZZZZZZZZZ.json"
  codMun = getFile(url,filename)
  #needed to make the encoding explicit after some problems with EL PEN~ON ANTIOQUIA
  #print(codMun.encoding)
  codMun = json.loads(codMun)
  table = []
  for j in range(len(codMun["mun"])) :
    reg = []
    name = str(codMun["mun"][j]["n"])
    reg.append(codMun["mun"][j]["c"])
    reg.append(name)
    table.append(reg)
  
  return table

# Execute this just once!!! It takes too long!!!
#------------------------------------------------------------------------------
dataKeys = []
table = []
sinConsulados = [ i for i in dptoCodes if i != '88']

# Example to get all mun data from  dptoCode
for cdp in sinConsulados:
  
  munsCodeNames = getMuns(cdp)
  # get only the codes (without name)
  munsCodes = [i[0] for i in munsCodeNames]
  munNames = [i[1] for i in munsCodeNames]

  k = 0 # Mmmm... Horrible hack
  for i in munsCodes :
    print("Downloading",cdp,':',getDpto(cdp), i,':',munNames[k])
    reg = []
    reg.append(cdp) #dptoCode
    reg.append(i) #munCode
    reg.append(munNames[k])
    k += 1 # end Horrible hack
    
    url = "https://presidente2018.registraduria.gov.co/resultados/data/PR/"
    filename = "D"+str(cdp)+i+"ZZZZZZZZZZZZ.json"
    
    munData = getFile(url,filename)
    munData = json.loads(munData)
    
    # Then we load everything for each municipality
    dataKeys = ['NEN','HMS','MTO','MES','PME','CEN','TNM','PTN',
                'VOT','PVO','ABS','PAB','VBL','PVB','VVA','PVV',
                'VNU','PVN','VCA','PVC']
  
    for j in dataKeys :
      reg.append(int(munData['generales']['escrutinio'][j]))
      
    reg.append(munData['candidatos']) # and put all 'candidatos' info in one cell :D
    table.append(reg)

dataKeys.insert(0,'CDP')
dataKeys.insert(1,'munCode')
dataKeys.insert(2,'munName')
dataKeys.append('candidatos')
#------------------------------------------------------------------------------
    
dfMun = pd.DataFrame(table)

dfMun.columns = dataKeys

# You can check the DataFrame here
dfMun

# Returns the code of the municipality given the CDP of the state and its name
# db needs to passed through db = dfMun
def getMunCode(db,cdp,munName) :
  munCode = db.loc[(db['CDP'] == cdp) & (db['munName'] == str(munName))]['munCode'].iloc[0]
  return munCode

#getMunCode(dfMun,"88","SUECIA") # can be compared with dfMun output

# return CCA given the CDP and  munName
# CCA is the code of the candidate who has 
# most of the votes in each municipality
# db = dfMun

def getWinner(db,cdp,munName) :
  
  candidatos = db.loc[
      (db['CDP'] == cdp) & (db['munName'] == str(munName))
  ]['candidatos'].iloc[0][0] # Index 0 contains the "winner" as seen from the API output
  
  candidatos = str(candidatos)
  candidatos = candidatos.replace("'",'"')
  candidatos = json.loads(candidatos)
  return candidatos["CCA"]

# Comparing strings is somewhat difficilt
# need to set the same encoding for both of the sources
# and wait for the better (they have no variation)

#print(getWinner(dfMun,"075","EL PEÃ‘ON"))
print(getWinner(dfMun,"17","RIOSUCIO"))
#print(dfMun)

# The same function as before but providing munCode
# instead of munName
def getWinnerBymunCode(db,cdp,munCode) :
  
  candidatos = db.loc[
      (db['CDP'] == cdp) & (db['munCode'] == munCode)
  ]['candidatos'].iloc[0][0]
  candidatos = str(candidatos)
  candidatos = candidatos.replace("'",'"')
  candidatos = json.loads(candidatos)
  return candidatos["CCA"]
  

print(getWinnerBymunCode(dfMun,"15","160"))

detailedMap = plt.figure(figsize=(10,10), dpi=90)
  
axis = detailedMap.add_subplot(111)


table = []

# Now we ask about the geometry for the map
# each .geoson file contains a description of each
# municipality in terms of a number of coordinates
# that allow us to plot them as a patch

for i in  sinConsulados:
  
  cca = dfNalStat.loc[dfNalStat['CDP'] == i ].iloc[0]['CCA']
  url = 'https://presidente2018.registraduria.gov.co/js/coords/'
  filename = i+".geojson"
  mapData = getFile(url,filename)
  mapData = json.loads(mapData)
  
  for j in range(len(mapData["features"])):
    
    reg = []
    reg.append(i) # CDP
    
    scaleFactor = 1
    munName = str(mapData["features"][j]["properties"]["name"])
    munCode = getMunCode(dfMun,i,munName)
    
    reg.append(munCode) # munCode
    reg.append(munName) # munName
    
    # get PVO for municipality
    munPVO = dfMun.loc[
      ( dfMun['CDP'] == i ) & (dfMun['munCode'] == munCode )
    ]['PVO'].iloc[0] * 1e-04;
    
    # get PVF for municipality
    munPVF = dfMun.loc[
          (dfMun["CDP"] == i) & (dfMun["munCode"] == munCode)
    ].iloc[0]["candidatos"][0]
    munPVF = str(munPVF).replace("'",'"') # So JSON can parse the string
    munPVF = json.loads(munPVF)
    munPVF = int(munPVF["PVF"])*1e-4
    
    #print( "Getting winner for", munName )
    cca = getWinner(dfMun,i,munName)
    
    if (mapData["features"][j]["geometry"]["type"] == "Polygon") :
      
      geoPoints = mapData["features"][j]["geometry"]["coordinates"][0];
      
      # Realsize and scaled
      drawMap(axis,geoPoints,
              scaleFactor=1,facecolor='WHITE',edgecolor='BLACK',linewidth=1)
      drawMap(axis,geoPoints,munPVF,getColor(cca),'WHITE')
      
      reg.append(geoPoints)
      
      # Bolivar CPA 05 had a MultiPolygon in it and its structure is different
      # Same with San Andres and Providencia Islands
    elif (mapData["features"][j]["geometry"]["type"] == "MultiPolygon") :
      
      #print("MultiPolygon found: ", getDpto(i) , munName)
      
      #for k in range(len(mapData["features"][j]["geometry"]["coordinates"][0])) :

      geoPoints = (mapData["features"][j]["geometry"]["coordinates"][0][0])

      drawMap(axis,geoPoints,1,"WHITE","BLACK",linewidth=1)
      drawMap(axis,geoPoints, munPVF, getColor(cca), "WHITE")
      #print("Adding",getDpto(i),munName)
      reg.append(geoPoints)
    else :
      
      print("Problem found: ",getDpto(i),mapData["features"][j]["properties"]["name"])
      
    
    print("Adding:", i, getDpto(i), munName , cca, munPVO)
    table.append(reg)
    
dfGeo = pd.DataFrame(table)
dfGeo.columns = ['CDP','munCode','munName','geoPoints']
axis.set_xlim([-80,-65])
axis.set_ylim([-4,13])
axis.set_aspect(1)

dfGeo

# with dfGeo we can redefine getMun
dfGeo = dfGeo.sort_values(by=['munName','CDP'], ascending=True)
dfGeo.reset_index(drop=True, inplace=True)
dfMun = dfMun.sort_values(by=['munName','CDP'], ascending=True)
dfMun.reset_index(drop=True, inplace=True)
dfMun["geoPoints"] = dfGeo["geoPoints"]

# gives a list of municipalities for a give cdp
# based on dfGeo
def getMunsOffline(cdp) :
  cdp = str(cdp).zfill(2)
  muns = dfGeo[
    (dfGeo['CDP'] == cdp)    
  ]['munCode']
  munList = [i for i in muns]
  return munList

detailedMap = plt.figure(figsize=(10,10), dpi=90)

axis = detailedMap.add_subplot(111)

sinConsulados = [ i for i in dptoCodes if i != '88']

for cdp in sinConsulados :
  
  munList = getMunsOffline(cdp)
  
  for mun in munList :
    
    geoPoints = dfGeo.loc[
        (dfGeo.CDP == cdp) &  (dfGeo.munCode == mun)
    ]['geoPoints'].iloc[0]

    drawMap(axis,geoPoints,
              scaleFactor=1,facecolor='WHITE',edgecolor='BLACK',linewidth=1)

axis.set_xlim([-80,-65])
axis.set_ylim([-4,13])
axis.set_aspect(1)

#output_notebook ()
output_file("mapa.html")

lons = []
lats = []
colors = []
munNames = []
ccas = []
dptoNames = []
pvfs = []
ccaNames = []
pabs = []

for index, row in dfMun.iterrows(): # Take out islands and embassies
  dptoCDP = str(row["CDP"])
  munCode = str(row["munCode"])
  
  munName = str(row["munName"]).capitalize()
  
  dptoNames.append(str(dfDpto.loc[
      dfDpto.CDP == dptoCDP
  ]['dptoName'].iloc[0]))
  
  cca = getWinnerBymunCode(dfMun,dptoCDP,munCode)
  ccas.append(cca) 
  ccaNames.append(getCCAName(cca))
  
  munPVF = dfMun.loc[
        (dfMun["CDP"] == dptoCDP) & (dfMun["munCode"] == munCode)
  ].iloc[0]["candidatos"][0]
  munPVF = str(munPVF).replace("'",'"') # So JSON can parse the string
  munPVF = json.loads(munPVF)
  munPVF = int(munPVF["PVF"])*1e-4
  pvfs.append(munPVF)
  
  # get PABs 
  munPAB = dfMun.loc[
    ( dfMun.CDP == dptoCDP ) & (dfMun.munCode == munCode )
  ]['PAB'].iloc[0] * 1e-04;
  pabs.append(munPAB)
  
  #print("Adding:", dptoCDP, munCode, munName,cca)
  colors.append(getColor(cca))
  munNames.append(munName)
  coords = row['geoPoints']
  #print(coords,munName)
  
  lons.append([coords[i][0] for i in range(len(coords))])
  lats.append([coords[i][1] for i in range(len(coords))])
  
source = ColumnDataSource(data=dict(
    x=lons,
    y=lats,
    colors=colors,
    name=munNames,
    cca=ccas,
    ccaName=ccaNames,
    dpto=dptoNames,
    pvf=pvfs,
    pab=pabs,
    
))

TOOLS = "pan,wheel_zoom,reset,hover,save"

p = figure(
    title="Elecciones Presidenciales\nPrimera Vuelta, 2018", 
    tools=TOOLS,
    match_aspect=True # ScaleX == ScaleY
)

p.patches('x', 'y', source=source,
          fill_color = 'colors',
          fill_alpha=0.5, line_color="white", line_width=0.5)

hover = p.select_one(HoverTool)
hover.point_policy = "follow_mouse"
hover.tooltips = [
    ('Dpto','@dpto'),
    ("Municipio", "@name"),
    ('CCA:','@ccaName'),
    ('PVF','@pvf'),
    ('PAB','@pab')
    
]

show(p)

# Upload html file to Drive
uploaded = drive.CreateFile({'title': 'mapa.html'})
uploaded.SetContentFile('mapa.html')
uploaded.Upload()

!ls

detailedMap = plt.figure(figsize=(10,10), dpi=90)

axis = detailedMap.add_subplot(111)

sinConsulados = [ i for i in dptoCodes if i != '88']

for cdp in sinConsulados :
  
  munList = getMunsOffline(cdp)
  
  for mun in munList :
    
    # get PVO for municipality
    munPVO = dfMun.loc[
      ( dfMun.CDP == cdp ) & (dfMun.munCode == mun )
    ]['PVO'].iloc[0] * 1e-04;
    
    # get PVF for municipality
    munPVF = dfMun.loc[
          (dfMun.CDP == cdp) & (dfMun.munCode == mun)
    ].iloc[0]["candidatos"][0]
    munPVF = str(munPVF).replace("'",'"') # So JSON can parse the string
    munPVF = json.loads(munPVF)
    munPVF = int(munPVF["PVF"])*1e-4
    
    # get PABs 
    munPAB = dfMun.loc[
      ( dfMun.CDP == cdp ) & (dfMun.munCode == mun )
    ]['PAB'].iloc[0] * 1e-04;
    
    cca = getWinnerBymunCode(dfMun,cdp,mun)
    
    geoPoints = dfGeo.loc[
        (dfGeo.CDP == cdp) &  (dfGeo.munCode == mun)
    ]['geoPoints'].iloc[0]

    drawMap(axis,geoPoints,
              scaleFactor=1,facecolor='WHITE',edgecolor='BLACK',linewidth=0)
    drawMap(axis,geoPoints,
              scaleFactor=munPVF,facecolor=getColor(cca),edgecolor='BLACK',linewidth=0)


axis.set_xlim([-80,-65])
axis.set_ylim([-4.3,13])
axis.set_aspect(1)

detailedMap = plt.figure(figsize=(10,10), dpi=90)

axis = detailedMap.add_subplot(111)

sinConsulados = [ i for i in dptoCodes if i != '88']

for cdp in sinConsulados :
  
  munList = getMunsOffline(cdp)
  
  for mun in munList :
    
    # get PVO for municipality
    munPVO = dfMun.loc[
      ( dfMun.CDP == cdp ) & (dfMun.munCode == mun )
    ]['PVO'].iloc[0] * 1e-04;
    
    # get PVF for municipality
    munPVF = dfMun.loc[
          (dfMun.CDP == cdp) & (dfMun.munCode == mun)
    ].iloc[0]["candidatos"][0]
    munPVF = str(munPVF).replace("'",'"') # So JSON can parse the string
    munPVF = json.loads(munPVF)
    munPVF = int(munPVF["PVF"])*1e-4
    
    # get PABs 
    munPAB = dfMun.loc[
      ( dfMun.CDP == cdp ) & (dfMun.munCode == mun )
    ]['PAB'].iloc[0] * 1e-04;
    
    cca = getWinnerBymunCode(dfMun,cdp,mun)
    
    geoPoints = dfGeo.loc[
        (dfGeo.CDP == cdp) &  (dfGeo.munCode == mun)
    ]['geoPoints'].iloc[0]

    drawMap(axis,geoPoints,
              scaleFactor=1,facecolor=getColor(cca),edgecolor='BLACK',linewidth=0.25)
    drawMap(axis,geoPoints,
              scaleFactor=(munPAB),facecolor='WHITE',edgecolor='BLACK',linewidth=0,alpha=1)


axis.set_xlim([-80,-65])
axis.set_ylim([-4.3,13])
axis.set_aspect(1)

#-------------------------------------------------------------
# the following function takes a polygon's area and retuns a scaleFactor
# that if scaled will produce a polygon of area normalizationFactor
# This is a "What if all the municipalities were represented by the same area and..."
# due to overlap problems it needs some more work
def normalize(area,normalizationFactor):
  scaleFactor = normalizationFactor/area
  # The transformation is done over a squared which implies the area is modified by a squared factor
  return math.sqrt(scaleFactor) 

detailedMap = plt.figure(figsize=(10,10), dpi=90)

axis = detailedMap.add_subplot(111)

sinConsulados = [ i for i in dptoCodes if i != '88']

for cdp in sinConsulados :
  
  munList = getMunsOffline(cdp)
  
  for mun in munList :
    
    # get PVO for municipality
    munPVO = dfMun.loc[
      ( dfMun.CDP == cdp ) & (dfMun.munCode == mun )
    ]['PVO'].iloc[0] * 1e-04;
    
    # get PVF for municipality
    munPVF = dfMun.loc[
          (dfMun.CDP == cdp) & (dfMun.munCode == mun)
    ].iloc[0]["candidatos"][0]
    munPVF = str(munPVF).replace("'",'"') # So JSON can parse the string
    munPVF = json.loads(munPVF)
    munPVF = int(munPVF["PVF"])*1e-4
    
    # get PABs 
    munPAB = dfMun.loc[
      ( dfMun.CDP == cdp ) & (dfMun.munCode == mun )
    ]['PAB'].iloc[0] * 1e-04;
    
    cca = getWinnerBymunCode(dfMun,cdp,mun)
    
    geoPoints = dfGeo.loc[
        (dfGeo.CDP == cdp) &  (dfGeo.munCode == mun)
    ]['geoPoints'].iloc[0]

    drawMap(axis,geoPoints,
              scaleFactor=1,facecolor=getColor(cca),edgecolor='BLACK',linewidth=0.25)


axis.set_xlim([-80,-65])
axis.set_ylim([-4.3,13])
axis.set_aspect(1)

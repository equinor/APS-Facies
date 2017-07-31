#!/bin/env python
# Python3  test preliminary preview 
#import roxar
import numpy as np 
import sys
import copy
import time
#import xml.etree.ElementTree as ET

import APSModel
import APSMainFaciesTable
import APSZoneModel
import APSGaussFieldJobs
import APSDataFromRMS
#import Trunc1D_xml
#import Trunc1D_A2_xml
#import Trunc2D_A_xml
#import Trunc2D_A2_xml
#import Trunc2D_B_xml
#import Trunc2D_B2_xml
#import Trunc2D_C_xml
import Trunc2D_Cubic_Overlay_xml
import Trunc2D_Angle_Overlay_xml
import Trunc3D_bayfill_xml
#import Trunc3D_A_xml
import Trend3D_linear_model_xml
#import generalFunctionsUsingRoxAPI as gr

import simGauss2D


from matplotlib import pyplot as plt 
import matplotlib
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from matplotlib.colors import LinearSegmentedColormap
#import scipy.ndimage

#import xml.etree.ElementTree as ET
#from  xml.etree.ElementTree import Element, SubElement, dump
#from xml.dom import minidom

import importlib

#importlib.reload(APSModel)
importlib.reload(APSZoneModel)
#importlib.reload(APSMainFaciesTable)
#importlib.reload(APSGaussFieldJobs)
#importlib.reload(APSDataFromRMS)

#importlib.reload(gr)
importlib.reload(simGauss2D)
#importlib.reload(Trunc1D_xml)
#importlib.reload(Trunc1D_A2_xml)
#importlib.reload(Trunc2D_A_xml)
#importlib.reload(Trunc2D_A2_xml)
#importlib.reload(Trunc2D_B_xml)
#importlib.reload(Trunc2D_B2_xml)
#importlib.reload(Trunc2D_C_xml)
#importlib.reload(Trunc2D_Cubic_Overlay_xml)
#importlib.reload(Trunc3D_bayfill_xml)
#importlib.reload(Trunc3D_A_xml)
#importlib.reload(Trend3D_linear_model_xml)



def defineColors(nFacies):
    # --- Colormaps from a list ---
    if nFacies == 2:
        colors = ['lawngreen','grey']
    elif nFacies == 3:
        colors = ['lawngreen','grey','dodgerblue']
    elif nFacies == 4:
        colors = ['lawngreen','grey','dodgerblue','gold']
    elif nFacies == 5:
        colors = ['lawngreen','grey','dodgerblue','gold','darkorchid']
    elif nFacies == 6:
        colors = ['lawngreen','grey','dodgerblue','gold','darkorchid','cyan']
    elif nFacies == 7:
        colors = ['lawngreen','grey','dodgerblue','gold','darkorchid','cyan','firebrick']
    elif nFacies == 8:
        colors = ['lawngreen','grey','dodgerblue','gold','darkorchid','cyan','firebrick','olivedrab']
    elif nFacies == 9:
        colors = ['lawngreen','grey','dodgerblue','gold','darkorchid','cyan','firebrick','olivedrab','blue']
    elif nFacies == 10:
        colors = ['lawngreen','grey','dodgerblue','gold','darkorchid','cyan','firebrick','olivedrab','blue','crimson']
    elif nFacies == 11:
        colors = ['lawngreen','grey','dodgerblue','gold','darkorchid','cyan','firebrick','olivedrab','blue','crimson','darkorange']
    elif nFacies == 12:
        colors = ['lawngreen','grey','dodgerblue','gold','darkorchid','cyan','firebrick','olivedrab','blue','crimson','darkorange','red']
    return colors

def writeFile(fileName,a):
    with open(fileName,'w') as file:
        count = 0
        text = ''
        outstring = ''
        for j in range(len(a)):
            text = text + str(a[j]) + '  '
            count += 1
            if count>=5:
                text = text + '\n'
                outstring += text
                count = 0
                text = ''
        if count > 0:
            outstring += text +'\n'
        file.write(outstring)
    print('Write file: ' + fileName)
    return

def readFile(fileName):
    print('Read file: ' + fileName)
    tmp = []
    with open(fileName,'r') as file:
        inString = file.read()
        words = inString.split()
        n = len(words)
        print('Number of values: ' + str(n))
        a = np.zeros(n,float)
        for i in range(len(words)):
            a[i] = float(words[i])

    return a


# Initialise common variables
functionName = 'testPreview.py'
rotatePlot = 0
useBestResolution = 1
noSim = 0  # Is set to 1 only if one don't want to simulate 2D fields (for test purpose only)
setWrite = 0 # Is set to 1 if write out simulated 2D fields
# --------- Main test program ----------------
print('matplotlib version: ' + matplotlib.__version__)
print('Run: testPreview')
modelFileName='APS.xml'
inputRMSDataFileName = 'rms_project_data_for_APS_gui.xml'
nArgv = len(sys.argv)
modelName = ' '
if nArgv > 1:
    modelName = sys.argv[1]

print('- Read file: ' + modelFileName)
apsModel      = APSModel.APSModel(modelFileName)
printInfo     = apsModel.printInfo()
zoneParamName  = apsModel.getZoneParamName()
mainFaciesTable = apsModel.getMainFaciesTable()

gridModelName = apsModel.getGridModelName()
previewZoneNumber = apsModel.getPreviewZoneNumber()

rmsData = APSDataFromRMS.APSDataFromRMS()
print('Read file: ' + inputRMSDataFileName)
rmsData.readRMSDataFromXMLFile(inputRMSDataFileName)
[nx, ny, x0, y0, previewDX, previewDY, xinc, yinc,previewTheta] = rmsData.getGridSize()

if useBestResolution:
    if nx < ny:
        nMin = nx
        nxPreview = nx
        # Use square pixels
        nyPreview = int(nxPreview*previewDY/previewDX)
    else:
        nMin = ny
        nyPreview = ny
        nxPreview = int(nyPreview*previewDX/previewDY)
else:
    if nx < ny:
        if ny > 600:
            nyPreview = 600
        else:
            nyPreview = ny
        nxPreview = int(nyPreview*previewDX/previewDY)
    else:
        if nx > 600:
            nxPreview = 600
        else:
            nyPreview = ny
        nyPreview = int(nxPreview*previewDY/previewDX)

print('nxPreview: ' + str(nxPreview))
print('nyPreview: ' + str(nyPreview))

#print('Theta: ' + str(180.0*theta/np.pi))
#print('CosTheta: ' + str(cosTheta))
#print('SinTheta: ' + str(sinTheta))
#print('LX: ' + str(DX))
#print('LY: ' + str(DY))


zoneNumber       = previewZoneNumber
zoneModel        = apsModel.getZoneModel(zoneNumber)
if zoneModel == None:
    print('Error: Zone number: ' + str(zoneNumber) + ' is not defined')
    sys.exit()
truncObject      = zoneModel.getTruncRule()
faciesNames      = zoneModel.getFaciesInZoneModel()
gaussFieldNames  = zoneModel.getUsedGaussFieldNames()
nFacies          = len(faciesNames)

nGaussFields     = len(gaussFieldNames)
useConstProb     = zoneModel.useConstProb()
cellNumber = 0
if useConstProb == 0:
    print('Error: Preview plots require constant facies probabilities')
    print('       Use arbitrary constant values')
#    cellIndicesForPreview = apsModel.getCellForPreview()
#    I = cellIndicesForPreview[0]
#    J = cellIndicesForPreview[1]
#    K = cellIndicesForPreview[2]
#    cellIndices = [I-1,J-1,K-1]
#    grid_indexer = grid.grid_indexer
#    cellNumber = grid_indexer.get_cell_numbers(cellIndices)
#    if printInfo >= 3:
#        text = 'Debug output: Cell indx for cell to be used to defined constant facies probabilities '
#        text = text + 'for previewer: ' + '(' + str(I) + ',' + str(J) + ',' + str(K) + ')' 
#        print(text)
#        print('Debug output: Cell number for cell indx (' + str(I) + ',' + str(J) + ',' + str(K) + ') is: '+ str(cellNumber)) 


faciesOrdering   = truncObject.getFaciesOrderIndexList()

probParamNames = []
faciesProb = []
print(' ')
print(' ---------  Zone number : ' + str(zoneNumber) + ' -----------------')
for fName in faciesNames:
    pName        = zoneModel.getProbParamName(fName)
    if useConstProb == 1:
        v = float(pName)
        p = int(v*1000+0.5)
        w = float(p)/1000.0
        print('Zone: ' + str(zoneNumber) + ' Facies: ' + fName + ' Prob: ' + str(w))
    else:
        v = 1.0/float(len(faciesNames))
#        print('Read prob param: ' + pName) 
#        [values] = gr.getContinuous3DParameterValues(gridModel,pName,realNumber,printInfo)
#        v = values[cellNumber]
        p = int(v*1000+0.5)
        w = float(p)/1000.0
        print('Zone: ' + str(zoneNumber) + ' Facies: ' + fName + ' Prob: ' + str(w))
    faciesProb.append(v)


            
                



# Calculate truncation map for given facies probabilities
#print('Facies prob:')
#print(repr(faciesProb))
truncObject.setTruncRule(faciesProb)

# Calculate polygons for truncation map for current facies probability
# as specified when calling setTruncRule(faciesProb)
[faciesPolygons]    = truncObject.truncMapPolygons()
[faciesIndxPerPolygon] = truncObject.faciesIndxPerPolygon()
#print('FaciesIndexPerPolygon:')
#print(repr(faciesIndxPerPolygon))
# Simulate three 2D gaussian fields
gaussFieldParamNamesToSimulate = gaussFieldNames
nx = int(nxPreview)
ny = int(nyPreview)
gridXSize = previewDX
gridYSize = previewDY
if noSim == 1:
    a1 = readFile('a1.dat')
    a2 = readFile('a2.dat')
    a3 = readFile('a3.dat')
else:
    [a1,a2,a3] = zoneModel.simGaussFieldWithTrendAndTransform(nx,ny,gridXSize,gridYSize,previewTheta)
    if setWrite == 1:
        print('Write 2D simulated gauss fields: ')
        writeFile('a1.dat',a1)
        writeFile('a2.dat',a2)
        writeFile('a3.dat',a3)

facies = np.zeros(nx*ny,int)
faciesFraction = np.zeros(nFacies,int)

for i in range(len(a1)):
    if nGaussFields == 1:
        phi1 = a1[i]
        [faciesCode,fIndx] = truncObject.defineFaciesByTruncRule(phi1)
    elif nGaussFields == 2:
        phi1 = a1[i]
        phi2 = a2[i]
        [faciesCode,fIndx] = truncObject.defineFaciesByTruncRule(phi1,phi2)
    elif nGaussFields == 3:
        phi1 = a1[i]
        phi2 = a2[i]
        phi3 = a3[i]
        [faciesCode,fIndx] = truncObject.defineFaciesByTruncRule(phi1,phi2,phi3)

    facies[i] = fIndx +1  # Use fIndx+1 as values in the facies plot 
    faciesFraction[fIndx] += 1

writeFile('facies2D.dat',facies)
print( ' ')
print( 'Facies name:   Simulated fractions:    Specified fractions:')
for i in range(nFacies):
    f = faciesFraction[i]
    fraction = float(f)/float(len(facies))
    print('{0:10}  {1:.3f}   {2:.3f}'.format(faciesNames[i],fraction,faciesProb[i]))
print( ' ' )


fmap  = np.reshape(facies,(ny,nx))  #Reshape to a 2D array with c-index ordering
amap1 = np.reshape(a1,(ny,nx))
amap2 = np.reshape(a2,(ny,nx)) 
amap3 = np.reshape(a3,(ny,nx)) 


# Plot the result
print( 'Make plots')
fig = plt.figure(figsize=[15.0, 10.0])

# Gauss1 transformed is plotted
ax = plt.subplot(2, 3, 1)
if rotatePlot:
    rot_im1 = scipy.ndimage.interpolation.rotate(amap1,previewTheta)
else:
    rot_im1 = amap1
im1 = ax.imshow(rot_im1, interpolation='none',aspect='equal',vmin=0.0,vmax=1.0,origin ='lower')

# Gauss2 transformed is plotted
ax = plt.subplot(2, 3, 2)
if rotatePlot:
    rot_im2 = scipy.ndimage.interpolation.rotate(amap2,previewTheta)
else:
    rot_im2 = amap2
im2 = ax.imshow(rot_im2, interpolation='none',vmin=0.0,vmax=1.0,origin = 'lower')


# Gauss3 transformed is plotted
ax = plt.subplot(2, 3, 3)
if rotatePlot:
    rot_im3 = scipy.ndimage.interpolation.rotate(amap3,previewTheta)
else:
    rot_im3 = amap3
im3 = ax.imshow(rot_im3, interpolation='none',vmin=0.0,vmax=1.0,origin = 'lower')


# Truncation map is plotted
ax = plt.subplot(2, 3, 4)

colors = defineColors(nFacies)

cmap_name = 'Colormap'
# Create the colormap
cm = matplotlib.colors.ListedColormap(colors,name=cmap_name,N=nFacies)
#cm = matplotlib.colors.ListedColormap(colors,name=cmap_name)
bounds = np.linspace(0.5,0.5+nFacies,nFacies+1)
#norm = matplotlib.colors.BoundaryNorm(bounds,cm.N)
#norm = matplotlib.colors.Normalize(vmin=0.5,vmax=nFacies+0.5)
#norm = matplotlib.colors.Normalize(vmin=0.99,vmax=float(nFacies)+0.01)
#bounds = np.linspace(0.0,float(nFacies),nFacies+1)
#ticks = []
#for i in range(nFacies+1):
#    t = 0.5 + i
#    ticks.append(t)

#print(repr(ticks))
ticks  = bounds
labels = faciesNames
#labels.append(' ')

colorNumberPerPolygon = []
patches = []
print('Number of facies:          ' + str(nFacies))
print('Number of facies polygons: ' + str(len(faciesPolygons)))
#print('Bounds: ')
#print(repr(bounds))
# print(repr(faciesPolygons))
maxfIndx = 0
colorForFacies = []
for i in range(len(faciesPolygons)):
    indx = faciesIndxPerPolygon[i]
    fIndx = faciesOrdering[indx]
    poly = faciesPolygons[i]
    polygon = Polygon(poly,closed=True,facecolor=colors[fIndx])
    ax.add_patch(polygon)
    fName = faciesNames[fIndx]
#    text = 'Polygon: ' + str(i) + ' ' + fName + ' Color: ' + colors[fIndx] 
#    text = text + ' Facies indx (zone): ' + str(fIndx)
    print('Polygon:{0:2d} Facies: {1:7}  Color: {2:12} Facies index(zone): {3:2d}'.format(i,fName,colors[fIndx],fIndx))
#    print(text)

#print(repr(colorNumberPerPolygon))


#maxfIndx = 0
#for i in range(len(faciesOrdering)):
#    fIndx = faciesOrdering[i]
#    if maxfIndx < fIndx:
#       maxfIndx = fIndx

#colorNumberPerPolygon.append(maxfIndx + 1)
#print('Color number per polygons: ' + repr(colorNumberPerPolygon))
#print('cm:')
#print(repr(cm))
#p = PatchCollection(patches,cmap=cm)
#p = PatchCollection(patches,alpha=0.99)
#p.set_array(np.array(colorNumberPerPolygon))
#fColors = p.get_facecolors()
#print('fColors: ' )
#print(repr(fColors))
#prp = p.properties()
#print(prp)
#print('Colornumberperpolygon:')
#print(repr(colorNumberPerPolygon))
#for i in range(len(p)):
#    pat = p[i]
#    p.set_facecolor(colorForFacies)
#colorArray = np.array(colorNumberPerPolygon)  
#print(repr(colorArray))  
#p.set_facecolor(colorForFacies)
#p.set_array(colorArray)
#p.set_clim([0,nFacies+1])
#fColors = p.get_facecolors()
#print('fColors: ' )
#print(repr(fColors))
#ax.add_collection(p)

# define binds and normalize
#N = nFacies
#bounds = np.linspace(0.5, N+0.5, N+1)

# norm = matplotlib.colors.BoundaryNorm(bounds, nFacies)



# Facies map is plotted
ax = plt.subplot(2, 3, 5)
if rotatePlot:
    rot_imFac = scipy.ndimage.interpolation.rotate(fmap,previewTheta)
else:
    rot_imFac = fmap
imFac = ax.imshow(rot_imFac, interpolation='none',cmap=cm,clim=(1,nFacies),origin='lower')


if nGaussFields >= 2:
    # Cross plot between G1 and G2
    ax = plt.subplot(2, 3, 6)
    plt.scatter(a1,a2,alpha=0.15,marker ='.',c='b')
    
# Color legend for the transformed Gaussian fields
cax1 = fig.add_axes([0.92,0.52,0.02,0.4])
fig.colorbar(im1,cax=cax1)

# Color legend for the truncation map and facies plots
cax2 = fig.add_axes([0.92,0.05,0.02,0.4])
fig.colorbar(imFac,cax=cax2, ticks=bounds+0.5, boundaries=bounds,drawedges=True)
cax2.set_yticklabels(labels)

#fig.colorbar(imFac,cax=cax2, spacing = 'proportional', norm=norm,ticks=bounds+0.5, boundaries=bounds,drawedges=True)
#plt.clim(0,nFacies+1)
#fig.colorbar(imFac,cax=cax2, spacing = 'proportional', ticks=bounds+0.5, boundaries=bounds)
#fig.colorbar(imFac,cax=cax2, spacing = 'proportional', ticks=bounds+0.5, boundaries=bounds,drawedges=True)
#fig.colorbar(imFac,cax=cax2,  ticks=bounds+0.5, boundaries=bounds,drawedges=True)
#fig.colorbar(imFac,cax=cax2,  ticks=ticks, boundaries = bounds,drawedges=True)


# Adjust subplots
plt.subplots_adjust(left=0.10, wspace=0.15, hspace=0.20,
                    bottom=0.05, top=0.92)
# Label the rows and columns of the table
if nArgv > 1:
    text = 'Model name: ' + modelName + '  Zone number: ' + str(zoneNumber)
else:
    text = 'Zone number: ' + str(zoneNumber)
fig.text(0.50, 0.98, text, ha='center')
fig.text(0.15, 0.95, "Gauss 1", ha='center')
fig.text(0.45, 0.95, "Gauss 2", ha='center')
fig.text(0.75, 0.95, "Gauss 3", ha='center')
fig.text(0.15, 0.46, "TruncMap", ha='center')
fig.text(0.45, 0.46, "Facies", ha='center')
fig.text(0.75, 0.46, "Crossplot G1,G2", ha='center')
for i in range(nFacies):
    p = int(faciesProb[i]*1000 + 0.5)
    faciesProb[i] = float(p)/1000.0
    text = faciesNames[i] +':  ' + str(faciesProb[i])
    fig.text(0.02,0.40-0.03*i, text,ha='left')
    
plt.show()
print('Finished testPreview')

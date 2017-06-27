import pickle
import pandas as pd
import numpy as np
import math
import json
import csv
import shapely.geometry as shp
from scipy.spatial import Voronoi

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection


thisRepo = '/home/mattdzugan/Documents/dev/Control Cities/'

interstates = pickle.load(open(thisRepo+"data/interim/InterstatesWithCityIDs.p","rb"))
cities = pd.DataFrame.from_csv(thisRepo+"data/Raw/uscitiesv1.2.csv", index_col=13)


## COMMONLY USED FUNCTIONS
def greatCircleDistance(lon1,lat1,lon2,lat2):
    deg2rad = math.pi/180.0
    lon1r = lon1*deg2rad
    lat1r = lat1*deg2rad
    lon2r = lon2*deg2rad
    lat2r = lat2*deg2rad
    if (abs(lon1-lon2)+abs(lat1-lat2)>0.0000001):
        centralAngle = math.acos( math.sin(lat1r)*math.sin(lat2r) + math.cos(lat1r)*math.cos(lat2r)*math.cos(lon2r-lon1r)  )
    else:
        centralAngle = 0
    return centralAngle*6378
def bearing(lon1,lat1,lon2,lat2):
    deg2rad = math.pi/180.0
    lon1r = lon1*deg2rad
    lat1r = lat1*deg2rad
    lon2r = lon2*deg2rad
    lat2r = lat2*deg2rad
    y = math.sin(lon2r-lon1r)*math.cos(lat2r)
    x = math.cos(lat1r)*math.sin(lat2r) - math.sin(lat1r)*math.cos(lat2r)*math.cos(lon2r-lon1r)
    b = math.atan2(y, x)/deg2rad
    return b




## start the main code
###############################################################################
## Run the models across I55 only #############################################
###############################################################################

# First determine all of the cities the end up being predicted on I55
interstate = interstates.loc[0]
pathFrame = interstate['Path']
N = len(pathFrame.index)
previousDist = -999
predictedCities = []
for jdx, coordinate in pathFrame.iterrows():
    print(jdx)
    mySegmentLon = pathFrame['lon'][jdx]
    mySegmentLat = pathFrame['lat'][jdx]
    mySegmentDist = pathFrame['dist'][jdx]
    mySegmentID = pathFrame['pointID'][jdx]
    distToPrev = mySegmentDist-previousDist
    
    if (distToPrev>8.04):
        truth = {}
        for direction in ['destWith', 'destAgainst']:
            citiesForNow = []                
            if (direction+'_UniqueNameDests') in pathFrame.columns:
                myDestIDs = pathFrame[(direction+'_UniqueNameDests')][jdx] #_consolidatedDestIDs
            else:
                myDestIDs = []
            # it's worth doing if there's at least 1 non-zero thing
            if (len(myDestIDs)>0):
                if (max(myDestIDs)>0):
                    previousDist = mySegmentDist
                    if (direction=='destWith'):
                        endPointLon = pathFrame['lon'][N-1]
                        endPointLat = pathFrame['lat'][N-1]
                    else:
                        endPointLon = pathFrame['lon'][0]
                        endPointLat = pathFrame['lat'][0]
                    bearingToEnd = bearing(mySegmentLon,mySegmentLat,endPointLon,endPointLat)
                    for cdx, city in cities.iterrows():
                        cityLon = city['lng']
                        cityLat = city['lat']
                        cityPop = city['population']
                        if cityPop>0:
                            bearingToCity = bearing(mySegmentLon,mySegmentLat,cityLon,cityLat)
                            a = abs(bearingToEnd-bearingToCity)
                            angleBetween = abs(((a+180)%360)-180)
                            if angleBetween<60:
                                distToCity = greatCircleDistance(mySegmentLon,mySegmentLat,cityLon,cityLat)
                                if ((distToCity<50)|(angleBetween<20)):
                                    cityForNow = {'id':cdx, 'pop':cityPop, 'dist':distToCity}
                                    cityForNow['sound'] = (cityPop/(distToCity**2))
                                    cityForNow['light'] = ((cityPop**2)/(distToCity**2))
                                    cityForNow['capac'] = ((cityPop**2)/(distToCity))
                                    cityForNow['mntSz'] = math.atan2(math.sqrt(cityPop),distToCity)
                                    cityForNow['mntHt'] = math.atan2(cityPop,distToCity)
                                    citiesForNow.append( cityForNow )                          
                    if len(citiesForNow)>0:
                        citiesForNow = sorted(citiesForNow, key=lambda k: k['sound'], reverse=True)
                        predictedCities.append(citiesForNow[0]['id'])                    
                        citiesForNow = sorted(citiesForNow, key=lambda k: k['light'], reverse=True)
                        predictedCities.append(citiesForNow[0]['id'])                  
                        citiesForNow = sorted(citiesForNow, key=lambda k: k['capac'], reverse=True)
                        predictedCities.append(citiesForNow[0]['id'])                   
                        citiesForNow = sorted(citiesForNow, key=lambda k: k['mntSz'], reverse=True)
                        predictedCities.append(citiesForNow[0]['id'])                   
                        citiesForNow = sorted(citiesForNow, key=lambda k: k['mntHt'], reverse=True)                    
                        predictedCities.append(citiesForNow[0]['id'])
                        citiesForNowClose = [x for x in citiesForNow if x['dist'] < 805] #500 miles
                        citiesForNowClose = sorted(citiesForNowClose, key=lambda k: k['pop'], reverse=True)  
                        if len(citiesForNowClose)>0:
                            predictedCities.append(citiesForNowClose[0]['id'])
                        citiesForNowClose = [x for x in citiesForNow if x['dist'] < 322] #200 miles
                        citiesForNowClose = sorted(citiesForNowClose, key=lambda k: k['pop'], reverse=True)  
                        if len(citiesForNowClose)>0:
                            predictedCities.append(citiesForNowClose[0]['id'])
                        citiesForNowClose = [x for x in citiesForNow if x['dist'] < 161] #100 miles
                        citiesForNowClose = sorted(citiesForNowClose, key=lambda k: k['pop'], reverse=True)  
                        if len(citiesForNowClose)>0:
                            predictedCities.append(citiesForNowClose[0]['id'])
predictedCities = list(set(predictedCities))
with open(thisRepo+"data/interim/citiesAlongI55.json", 'wb') as outfile:
    json.dump(predictedCities, outfile)  



with open(thisRepo+"data/interim/citiesAlongI55.json") as json_data:
     predictedCities = json.load(json_data)
 

# Then filter down the list of cities to only those in I55 predictions
relevantCities = cities.loc[predictedCities]     


# Then go through mile by mile and print a list of each cities' {id, name, dist, angle, pop}
simulation = []
interstate = interstates.loc[0]
pathFrame = interstate['Path']
N = len(pathFrame.index)
previousDist = -999
for jdx, coordinate in pathFrame.iterrows():
    print(jdx)
    citiesNow = []
    mySegmentLon = round(pathFrame['lon'][jdx],3)
    mySegmentLat = round(pathFrame['lat'][jdx],3)
    mySegmentDist = pathFrame['dist'][jdx]
    mySegmentID = pathFrame['pointID'][jdx]
    segment = {'idx':jdx, 'id':mySegmentID, 'lat':mySegmentLat, 'lon':mySegmentLon}
    distToPrev = mySegmentDist-previousDist
    if (distToPrev>8.04):
        direction = 'destAgainst'
        if (direction+'_UniqueNameDests') in pathFrame.columns:
            myDestIDs = pathFrame[(direction+'_UniqueNameDests')][jdx] #_consolidatedDestIDs
        else:
            myDestIDs = []
        # it's worth doing if there's at least 1 non-zero thing
        if (len(myDestIDs)>0):
            if (max(myDestIDs)>0):
                previousDist = mySegmentDist
                endPointLon = pathFrame['lon'][0]
                endPointLat = pathFrame['lat'][0]
                bearingToEnd = bearing(mySegmentLon,mySegmentLat,endPointLon,endPointLat)
                for cdx, city in relevantCities.iterrows():
                    cityLon = city['lng']
                    cityLat = city['lat']
                    cityPop = city['population']
                    if cityPop>0:
                        bearingToCity = bearing(mySegmentLon,mySegmentLat,cityLon,cityLat)
                        a = (bearingToEnd-bearingToCity)
                        angleBetween = (((a+180)%360)-180)
                        if abs(angleBetween)<60:
                            distToCity = greatCircleDistance(mySegmentLon,mySegmentLat,cityLon,cityLat)
                            if ((distToCity<50)|(abs(angleBetween)<20)):
                                cityNow = {'id':cdx}
                                cityNow['name'] = city.city_ascii
                                cityNow['pop'] = int(cityPop)
                                cityNow['dist'] = round(distToCity,2)
                                cityNow['angle'] = round(a,2) #angleBetween
                                citiesNow.append(cityNow)
                citiesNow = sorted(citiesNow, key=lambda k: k['dist'], reverse=True)
                segment['cities'] = citiesNow
                simulation.append(segment)
simulation = list(reversed(simulation))
with open(thisRepo+"report/data/simulationDemo.json", 'wb') as outfile:
    json.dump(simulation, outfile)  


###############################################################################
## Run the models across ALL INTERSTATES ######################################
###############################################################################

models = []
for idx, interstate in interstates.iterrows():
    #if (idx>0):
    #   break
    pathFrame = interstate['Path']
    N = len(pathFrame.index)
    print("##############"+str(idx))
    thisInterstateBookedYet = []
    previousDist = -999
    thisInterstateJson = {'id':idx}
    thisPath = []
    for jdx, coordinate in pathFrame.iterrows():
        print(jdx)
        mySegmentLon = pathFrame['lon'][jdx]
        mySegmentLat = pathFrame['lat'][jdx]
        mySegmentDist = pathFrame['dist'][jdx]
        mySegmentID = pathFrame['pointID'][jdx]
        distToPrev = mySegmentDist-previousDist
        
        
        
        
        if (distToPrev>8.04):
            truth = {}
            for direction in ['destWith', 'destAgainst']:
                citiesForNow = []                
                if (direction+'_UniqueNameDests') in pathFrame.columns:
                    myDestIDs = pathFrame[(direction+'_UniqueNameDests')][jdx] #_consolidatedDestIDs
                else:
                    myDestIDs = []
                
                # it's worth doing if there's at least 1 non-zero thing
                if (len(myDestIDs)>0):
                    if (max(myDestIDs)>0):
                        previousDist = mySegmentDist
                        if (direction=='destWith'):
                            endPointLon = pathFrame['lon'][N-1]
                            endPointLat = pathFrame['lat'][N-1]
                        else:
                            endPointLon = pathFrame['lon'][0]
                            endPointLat = pathFrame['lat'][0]
                        bearingToEnd = bearing(mySegmentLon,mySegmentLat,endPointLon,endPointLat)
                        for cdx, city in cities.iterrows():
                            #if (cdx>1840001000):
                            #    break
                            cityLon = city['lng']
                            cityLat = city['lat']
                            cityPop = city['population']
                            if cityPop>0:
                                bearingToCity = bearing(mySegmentLon,mySegmentLat,cityLon,cityLat)
                                a = abs(bearingToEnd-bearingToCity)
                                angleBetween = abs(((a+180)%360)-180)
                                if angleBetween<60:
                                    distToCity = greatCircleDistance(mySegmentLon,mySegmentLat,cityLon,cityLat)
                                    if ((distToCity<50)|(angleBetween<20)):
                                        cityForNow = {'id':cdx, 'pop':cityPop, 'dist':distToCity}
                                        cityForNow['sound'] = (cityPop/(distToCity**2))
                                        cityForNow['light'] = ((cityPop**2)/(distToCity**2))
                                        cityForNow['capac'] = ((cityPop**2)/(distToCity))
                                        cityForNow['mntSz'] = math.atan2(math.sqrt(cityPop),distToCity)
                                        cityForNow['mntHt'] = math.atan2(cityPop,distToCity)
                                        citiesForNow.append( cityForNow )
                        leaders = {}
                        
                        citiesForNow = sorted(citiesForNow, key=lambda k: k['sound'], reverse=True)
                        if len(citiesForNow)>0:
                            leaders['sound'] = citiesForNow[0]['id']
                        else:
                            leaders['sound'] = -999
                        
                        citiesForNow = sorted(citiesForNow, key=lambda k: k['light'], reverse=True)
                        if len(citiesForNow)>0:
                            leaders['light'] = citiesForNow[0]['id']
                        else:
                            leaders['light'] = -999
                        
                        citiesForNow = sorted(citiesForNow, key=lambda k: k['capac'], reverse=True)
                        if len(citiesForNow)>0:
                            leaders['capac'] = citiesForNow[0]['id']
                        else:
                            leaders['capac'] = -999
                        
                        citiesForNow = sorted(citiesForNow, key=lambda k: k['mntSz'], reverse=True)
                        if len(citiesForNow)>0:
                            leaders['mntSz'] = citiesForNow[0]['id']
                        else:
                            leaders['mntSz'] = -999
                        
                        citiesForNow = sorted(citiesForNow, key=lambda k: k['mntHt'], reverse=True)
                        if len(citiesForNow)>0:
                            leaders['mntHt'] = citiesForNow[0]['id']
                        else:
                            leaders['mntHt'] = -999
                        
                        if len(citiesForNow)>0:
                            citiesForNowClose = [x for x in citiesForNow if x['dist'] < 805] #500 miles
                            citiesForNowClose = sorted(citiesForNowClose, key=lambda k: k['pop'], reverse=True)  
                            if len(citiesForNowClose)>0:
                                leaders['max5H'] = citiesForNowClose[0]['id']
                            else:
                                leaders['max5H'] = -999
                            citiesForNowClose = [x for x in citiesForNow if x['dist'] < 322] #200 miles
                            citiesForNowClose = sorted(citiesForNowClose, key=lambda k: k['pop'], reverse=True)  
                            if len(citiesForNowClose)>0:
                                leaders['max2H'] = citiesForNowClose[0]['id']
                            else:
                                leaders['max2H'] = -999
                            citiesForNowClose = [x for x in citiesForNow if x['dist'] < 161] #100 miles
                            citiesForNowClose = sorted(citiesForNowClose, key=lambda k: k['pop'], reverse=True)  
                            if len(citiesForNowClose)>0:
                                leaders['max1H'] = citiesForNowClose[0]['id']
                            else:
                                leaders['max1H'] = -999
                        else:
                            leaders['max5H'] = -999
                            leaders['max2H'] = -999
                            leaders['max1H'] = -999
                            
                        isTrue = {}
                        isTrue['sound'] = (str(leaders['sound']) in myDestIDs)
                        isTrue['light'] = (str(leaders['light']) in myDestIDs)
                        isTrue['capac'] = (str(leaders['capac']) in myDestIDs)
                        isTrue['mntSz'] = (str(leaders['mntSz']) in myDestIDs)
                        isTrue['mntHt'] = (str(leaders['mntHt']) in myDestIDs)
                        isTrue['max5H'] = (str(leaders['max5H']) in myDestIDs)
                        isTrue['max2H'] = (str(leaders['max2H']) in myDestIDs)
                        isTrue['max1H'] = (str(leaders['max1H']) in myDestIDs)
                        
                        truth[direction] = isTrue
                        
                        #print('SOUND guessed:   '+cities.loc[leaders['sound']].city_ascii+'       '+str(isTrue['sound']))
                        #print('LIGHT guessed:   '+cities.loc[leaders['light']].city_ascii+'       '+str(isTrue['light']))
                        #print('CAPAC guessed:   '+cities.loc[leaders['capac']].city_ascii+'       '+str(isTrue['capac']))
                        #print('MNTSZ guessed:   '+cities.loc[leaders['mntSz']].city_ascii+'       '+str(isTrue['mntSz']))
                        #print('MNTHT guessed:   '+cities.loc[leaders['mntHt']].city_ascii+'       '+str(isTrue['mntHt']))
                        #print('MAX5H guessed:   '+cities.loc[leaders['max5H']].city_ascii+'       '+str(isTrue['max5H']))
                        #print('MAX2H guessed:   '+cities.loc[leaders['max2H']].city_ascii+'       '+str(isTrue['max2H']))
                        #print('MAX1H guessed:   '+cities.loc[leaders['max1H']].city_ascii+'       '+str(isTrue['max1H']))
            thisPath.append({'id':jdx, 'pid':mySegmentID, 'truths':truth})                
    thisInterstateJson['path'] = thisPath
    models.append(thisInterstateJson)
with open(thisRepo+"data/interim/modelResults.json", 'wb') as outfile:
    json.dump(models, outfile)  
                               
with open(thisRepo+"data/interim/modelResults.json") as json_data:
     models = json.load(json_data)            
                
###############################################################################
## Summarize the modelResults for Histograms ##################################
###############################################################################

counts = {'Count':0,            'sound':0,  'light':0,  'capac':0,  'mntSz':0,  'mntHt':0,  'max5H':0,  'max2H':0,  'max1H':0}
hists  = {'names':[],'dirs':[], 'sound':[], 'light':[], 'capac':[], 'mntSz':[], 'mntHt':[], 'max5H':[], 'max2H':[], 'max1H':[]}                
for interstate in models:
    actualInterstate = interstates.loc[interstate['id']]
    path = interstate['path']
    myName = actualInterstate['Name']
    myOrientation = actualInterstate['Direction']
    N = len(path)
    for direction in ['destWith', 'destAgainst']:
        if (myOrientation=='South'):
            if (direction=='destWith'):
                myDir = 'Southbound'
            else:
                myDir = 'Northbound'
        else:
            if (direction=='destWith'):
                myDir = 'Eastbound'
            else:
                myDir = 'Westbound'
        N_thisDir = 0
        counts_thisDir = {'sound':0, 'light':0, 'capac':0, 'mntSz':0, 'mntHt':0, 'max5H':0, 'max2H':0, 'max1H':0}
        for ii in range(N):
            seg = path[ii]
            truths = seg['truths']
            if direction in truths.keys():
                m = truths[direction]
                N_thisDir += 1
                counts_thisDir['sound'] += int(m['sound'])
                counts_thisDir['light'] += int(m['light'])
                counts_thisDir['capac'] += int(m['capac'])
                counts_thisDir['mntSz'] += int(m['mntSz'])
                counts_thisDir['mntHt'] += int(m['mntHt'])
                counts_thisDir['max5H'] += int(m['max5H'])
                counts_thisDir['max2H'] += int(m['max2H'])
                counts_thisDir['max1H'] += int(m['max1H'])
        # if it's big enough, add it to hist
        if (N_thisDir>20):
            hists['names'].append(myName)
            hists['dirs'].append(myDir)
            hists['sound'].append(counts_thisDir['sound']/float(N_thisDir))
            hists['light'].append(counts_thisDir['light']/float(N_thisDir))
            hists['capac'].append(counts_thisDir['capac']/float(N_thisDir))
            hists['mntSz'].append(counts_thisDir['mntSz']/float(N_thisDir))
            hists['mntHt'].append(counts_thisDir['mntHt']/float(N_thisDir))
            hists['max5H'].append(counts_thisDir['max5H']/float(N_thisDir))
            hists['max2H'].append(counts_thisDir['max2H']/float(N_thisDir))
            hists['max1H'].append(counts_thisDir['max1H']/float(N_thisDir))
        # add everything to the master count list
        counts['Count'] += N_thisDir
        counts['sound'] += counts_thisDir['sound']
        counts['light'] += counts_thisDir['light']
        counts['capac'] += counts_thisDir['capac']
        counts['mntSz'] += counts_thisDir['mntSz']
        counts['mntHt'] += counts_thisDir['mntHt']
        counts['max5H'] += counts_thisDir['max5H']
        counts['max2H'] += counts_thisDir['max2H']
        counts['max1H'] += counts_thisDir['max1H']
                     
overview = []
histData = []
for method in ['sound','light','capac','mntSz','mntHt','max5H','max2H','max1H']:
    thisMethod = {'method':method}
    thisMethod['mean'] = counts[method]/float(counts['Count'])
    thisMethod['Q1'] =   np.percentile(np.array(hists[method]),25)
    thisMethod['Q2'] =   np.percentile(np.array(hists[method]),50)
    thisMethod['Q3'] =   np.percentile(np.array(hists[method]),75)
    #thisMethod['data'] = hists[method]
    overview.append(thisMethod)
    for ii in range(len(hists[method])):
        histData.append({'method':method, 'val':hists[method][ii], 'name':hists['names'][ii], 'dir':hists['dirs'][ii]})
with open(thisRepo+"report/data/modelResultsOverview.json", 'wb') as outfile:
    json.dump(overview, outfile)  
                
with open(thisRepo+"report/data/modelResultsOverview.csv", 'wb') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(['method','value','name','dir'])    
    for entry in histData:
        csvwriter.writerow([entry['method'], entry['val'], entry['name'], entry['dir']])
           
                
                
                               
###############################################################################
## Process the results for miniature maps #####################################
###############################################################################
                               
# # build the voronoi                               
interstates = pickle.load(open(thisRepo+"data/interim/InterstatesWithCityIDs.p","rb"))
CONUS_lonlat = np.loadtxt(open(thisRepo+"/data/Raw/CONUS.geo.csv", "rb"), delimiter=",", skiprows=1)
CONUS_poly = shp.Polygon(CONUS_lonlat)
CONUS_box = np.array([  [-180.0,90.0],
                        [180.0, 90.0],
                        [180.0, -90.0],
                        [-180.0,-90.0] ])
#CONUS_lonlat

interstateLonLats = np.empty([0,2])
interstatePointIDs = []
for model in models:
    thisInterstateId = model['id']
    thisPath = model['path']
    actualInterstate = interstates.loc[thisInterstateId]
    actualPath = actualInterstate['Path']
    for seg in thisPath:
        pathIndex = seg['id']
        globalIndex = seg['pid']
        thisLon = actualPath.loc[pathIndex,'lon']
        thisLat = actualPath.loc[pathIndex,'lat']
        thisPID = actualPath.loc[pathIndex,'pointID']
        if (not (int(globalIndex)==int(thisPID))):
            print("uh oh")
        thisLonLat = np.array([thisLon,thisLat])
        interstateLonLats = np.vstack((interstateLonLats,thisLonLat))
        interstatePointIDs = np.hstack((interstatePointIDs,thisPID))

points = np.vstack((interstateLonLats,CONUS_box))
vor = Voronoi(points)
#voronoi_plot_2d(vor)
#plt.show()
fig, ax = plt.subplots()
patches = []
interstatePolygons = []
interstatePointAreas = np.empty([interstateLonLats.shape[0],1])
for ii in range(interstateLonLats.shape[0]):
    p_r = vor.point_region[ii]
    myVertIDs = vor.regions[p_r]
    myVerts = vor.vertices[myVertIDs]

    myIntersectVerts = CONUS_poly.intersection(shp.Polygon(myVerts))
    interstatePolygons.append(myIntersectVerts)
    interstatePointAreas[ii] = (myIntersectVerts.area)*(111*111*math.cos(math.radians(interstateLonLats[ii,1])))
    #print(myIntersectVerts)
    if (myIntersectVerts.geom_type == 'Polygon'):
        patches.append(Polygon(myIntersectVerts.exterior.coords,True))

VoronoiResults = {  'PointID':interstatePointIDs,
                    'Polygon':interstatePolygons,
                    'Areas':interstatePointAreas}
pickle.dump(VoronoiResults, open(thisRepo + "data/interim/modelVoronoi.p", "wb"))
#
#p = PatchCollection(patches, cmap=matplotlib.cm.jet, alpha=0.4)
#colors = 100*np.random.rand(len(patches))
#p.set_array(np.array(colors))
#ax.add_collection(p)
#ax.set_xlim(-130, -60)
#ax.set_ylim(20, 60)
#plt.show()
                
# # build the shape list                
VoronoiResults = pickle.load(open(thisRepo+"data/interim/modelVoronoi.p","rb"))
truthinessDict = {}
for method in ['sound', 'light', 'capac', 'mntSz', 'mntHt', 'max5H', 'max2H', 'max1H']:
    for model in models:
        idx = model['id']
        #if (idx>20):
        #    break
        print("##############"+str(idx))
    
        path = model['path']
        L = len(path)
        # go through path, 
        # determining if each segment is a 0=(all false), 1=(half true), 2=(all true)
        for ii in range(L):
            Numerator = 0
            Denominator = 0
            if 'destWith' in path[ii]['truths']:
                Denominator += 1 
                if path[ii]['truths']['destWith'][method]:
                    Numerator += 1 
            if 'destAgainst' in path[ii]['truths']:
                Denominator += 1  
                if path[ii]['truths']['destAgainst'][method]:
                    Numerator += 1 
                    
            if (Denominator==1):
                if (Numerator==1):
                    path[ii]['truthiness'] = 2
                else:
                    path[ii]['truthiness'] = 0
                path[ii]['truthiness'] = 0
            else:
                path[ii]['truthiness'] = int(Numerator)
            
        # for each city, find each leg and its length
        legs = []
        # # With
        for tt in [0, 1, 2]:
            inLeg = False
            for ii in range(L):
                myTruthiness = path[ii]['truthiness']
                if (int(myTruthiness) == int(tt)):
                    if inLeg:
                        if (ii<(L-1)):
                            # keep the leg alive
                            inLeg = True
                        else:
                            # close out the leg
                            myStart = leg['StartIndex']
                            myStop = path[ii]['id'] - 1
                            leg['StopIndex'] = myStop
                            legs.append(leg)
                            inLeg = False
                    else:
                        #start a new leg
                        leg = {'truthiness':tt, 'StartIndex':path[ii]['id']}
                        inLeg = True
                else:
                    if inLeg:
                        # close out the leg
                        myStart = leg['StartIndex']
                        myStop = path[ii]['id'] - 1
                        leg['StopIndex'] = myStop
                        legs.append(leg)
                        inLeg = False
                    else: 
                        # keep waiting
                        inLeg = False
        
        
         
        # for each leg, add it to the truthiness
        for leg in legs:
            tID = leg['truthiness']
            tStartIndx = leg['StartIndex']
            tStopIndx  = leg['StopIndex']
            if not truthinessDict.has_key(str(tID)):
                newTruthiness = {'id':tID, 'Legs':[]}
                truthinessDict[str(tID)] = newTruthiness
            newLeg = {'Start':tStartIndx, 'Stop':tStopIndx, 'highway':idx}
            ListOfLegs = truthinessDict[str(tID)]['Legs']
            ListOfLegs.append(newLeg)
        hi = 0
        hi = 0
        hi = 0
        hi = 0
    for tt in [0, 1, 2]:
        lineGeometries = []
        areaGeometries = []
        ListOfLegs = truthinessDict[str(tt)]['Legs']
        for leg in ListOfLegs:
            highwayID = leg['highway']
            interstate = interstates.loc[highwayID]
            pathFrame = interstate['Path']
            a = min(leg['Start'],leg['Stop'])
            b = max(leg['Start'],leg['Stop'])
            
            thisLine = []
            #initialize region
            coord = pathFrame.iloc[a]
            pID = int(coord['pointID'])
            pInd = np.argwhere(VoronoiResults['PointID']==pID)[0][0]
            buildingRegion = VoronoiResults['Polygon'][pInd]
            for ind in range(a,b):
                coord = pathFrame.iloc[ind]
                mylon = round(coord.lon,4)
                mylat = round(coord.lat,4)
                thisLine.append([mylon, mylat])
                pID = int(coord['pointID'])
                if pID in VoronoiResults['PointID']:
                    pInd = np.argwhere(VoronoiResults['PointID']==pID)[0][0]
                    thisVor = VoronoiResults['Polygon'][pInd]
                    buildingRegion = buildingRegion.union(thisVor)
            #simplify the line if possible for smaller filesize
            if (len(thisLine)>1):
                line = shp.LineString(thisLine)
                simpleLine = line.simplify(0.035) #5 miles = 8 km = 0.07 deg
                thisLine = simpleLine.coords[:]
            #simpleRegion = buildingRegion.simplify(0.0005) 
            simpleRegion = buildingRegion.simplify(0.035)
            #simpleRegion = simpleRegion.buffer(0.1).buffer(-0.05)
            lineGeometries.append({'type':'LineString', 'coordinates':thisLine})
            areaGeometries.append(shp.mapping(simpleRegion))
        lineGeomCollection = {'type':'GeometryCollection', 'geometries':lineGeometries}
        areaGeomCollection = {'type':'GeometryCollection', 'geometries':areaGeometries}
        fullCollection = {'areas':areaGeomCollection,'lines':lineGeomCollection}
        with open(thisRepo+"report/data/modeling/"+method+"_"+str(tt)+".json", 'wb') as outfile:
            json.dump(fullCollection, outfile)






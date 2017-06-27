import pickle
import pandas as pd
import shapely.geometry as shp
import json

thisRepo = '/home/mattdzugan/Documents/dev/Control Cities/'

interstates = pickle.load(open(thisRepo+"data/interim/InterstatesWithCityIDs.p","rb"))
voronoiResults = pickle.load(open(thisRepo + "data/interim/InterstateVoronoi.p", "rb"))
cities = pd.DataFrame.from_csv(thisRepo+"data/Raw/uscitiesv1.2.csv", index_col=13)


cityDict = {}
cityListJSON = []


## for each interstate
## ## for each destination
## ## ## record start/stop info for that city

## for each city
## ## make one massive polygon
## ## make one massive polyline

for idx, interstate in interstates.iterrows():
    #if (idx>20):
    #    break
    print("##############"+str(idx))

    
    

    pathFrame = interstate['Path']
    # go through path, 
    # recording lat lons, 
    # but also keeping list of cities
    citiesWith = []
    citiesAgainst = []
    for jdx, coordinate in pathFrame.iterrows():
        # but also record the cities while i'm in here
        # # With
        if 'destWith_UniqueNameDests' in pathFrame.columns:
            myDestIDs = pathFrame['destWith_UniqueNameDests'][jdx] 
        else:
            myDestIDs = []
        for ddx in range(len(myDestIDs)):
            myDestID = int(myDestIDs[ddx])
            if ((myDestID>0)&(myDestID not in citiesWith)):
                citiesWith.append(myDestID)
        # # Against
        if 'destAgainst_UniqueNameDests' in pathFrame.columns:
            myDestIDs = pathFrame['destAgainst_UniqueNameDests'][jdx] 
        else:
            myDestIDs = []
        for ddx in range(len(myDestIDs)):
            myDestID = int(myDestIDs[ddx])
            if ((myDestID>0)&(myDestID not in citiesAgainst)):
                citiesAgainst.append(myDestID)    
        
    # for each city, find each leg and its length
    legsWith = []
    legsAgainst = []
    # # With
    for cc in citiesWith:
        if 'destWith_UniqueNameDests' in pathFrame.columns:
            inLeg = False
            for jdx, coordinate in pathFrame.iterrows():
                myDestIDs = pathFrame['destWith_UniqueNameDests'][jdx] 
                if str(cc) in myDestIDs:
                    if inLeg:
                        if (jdx<(pathFrame.shape[0]-1)):
                            # keep the leg alive
                            inLeg = True
                        else:
                            # close out the leg
                            myStart = leg['StartIndex']
                            myStop = jdx - 1
                            leg['StopIndex'] = myStop
                            leg['length'] = abs(pathFrame['dist'][myStart]-pathFrame['dist'][myStop])
                            legsWith.append(leg)
                            inLeg = False
                    else:
                        #start a new leg
                        myCityName = cities.loc[int(cc)].city_ascii
                        leg = {'cityID':cc, 'StartIndex':jdx, 'cityName':myCityName}
                        inLeg = True
                else:
                    if inLeg:
                        # close out the leg
                        myStart = leg['StartIndex']
                        myStop = jdx - 1
                        leg['StopIndex'] = myStop
                        leg['length'] = abs(pathFrame['dist'][myStart]-pathFrame['dist'][myStop])
                        legsWith.append(leg)
                        inLeg = False
                    else: 
                        # keep waiting
                        inLeg = False
    # # Against
    for cc in citiesAgainst:
        if 'destAgainst_UniqueNameDests' in pathFrame.columns:
            inLeg = False
            for jdx, coordinate in pathFrame.iterrows():
                myDestIDs = pathFrame['destAgainst_UniqueNameDests'][jdx] 
                if str(cc) in myDestIDs:
                    if inLeg:
                        if (jdx<(pathFrame.shape[0]-1)):
                            # keep the leg alive
                            inLeg = True
                        else:
                            # close out the leg
                            myStart = leg['StartIndex']
                            myStop = jdx - 1
                            leg['StopIndex'] = myStop
                            leg['length'] = abs(pathFrame['dist'][myStart]-pathFrame['dist'][myStop])
                            legsAgainst.append(leg)
                            inLeg = False
                    else:
                        #start a new leg
                        myCityName = cities.loc[int(cc)].city_ascii
                        leg = {'cityID':cc, 'StartIndex':jdx, 'cityName':myCityName}
                        inLeg = True
                else:
                    if inLeg:
                        # close out the leg
                        myStart = leg['StartIndex']
                        myStop = jdx - 1
                        leg['StopIndex'] = myStop
                        leg['length'] = abs(pathFrame['dist'][myStart]-pathFrame['dist'][myStop])
                        legsAgainst.append(leg)
                        inLeg = False
                    else: 
                        # keep waiting
                        inLeg = False
    
    
     
    # for each leg, add it to the city
    legsBothWays = legsWith+legsAgainst
    for leg in legsBothWays:
        cityName = leg['cityName']
        cityID = leg['cityID']
        cityStartIndx = leg['StartIndex']
        cityStopIndx  = leg['StopIndex']
        cityLen = leg['length']
        if not cityDict.has_key(str(cityID)):
            newCity = {'Name':cityName, 'Legs':[]}
            cityDict[str(cityID)] = newCity
            stateName = cities.loc[cityID].state_id
            cityPop = cities.loc[cityID].population
            mytext = cityName+', '+stateName
            cityListJSON.append({'id':cityID ,'text':mytext, 'city':cityName, 'state':stateName, 'pop':cityPop})
        newLeg = {'Start':cityStartIndx, 'Stop':cityStopIndx, 'Length':cityLen, 'highway':idx}
        ListOfLegs = cityDict[str(cityID)]['Legs']
        ListOfLegs.append(newLeg)
    
    
cityListJSON = sorted(cityListJSON, key=lambda k: k['pop'], reverse=True)

with open(thisRepo+"report/data/cityList.json", 'wb') as outfile:
        json.dump(cityListJSON, outfile)


for city in cityListJSON:
    lineGeometries = []
    areaGeometries = []
    ListOfLegs = cityDict[str(city['id'])]['Legs']
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
        buildingRegion = voronoiResults['Polygon'][pID]
        for ind in range(a,b):
            coord = pathFrame.iloc[ind]
            mylon = round(coord.lon,4)
            mylat = round(coord.lat,4)
            thisLine.append([mylon, mylat])
            pID = int(coord['pointID'])
            thisVor = voronoiResults['Polygon'][pID]
            buildingRegion = buildingRegion.union(thisVor)
        #simplify the line if possible for smaller filesize
        if (len(thisLine)>1):
            line = shp.LineString(thisLine)
            simpleLine = line.simplify(0.001)
            thisLine = simpleLine.coords[:]
        #simpleRegion = buildingRegion.simplify(0.0005) 
        simpleRegion = buildingRegion.simplify(0.005)
            
        lineGeometries.append({'type':'LineString', 'coordinates':thisLine})
        areaGeometries.append(shp.mapping(simpleRegion))
    lineGeomCollection = {'type':'GeometryCollection', 'geometries':lineGeometries}
    areaGeomCollection = {'type':'GeometryCollection', 'geometries':areaGeometries}
    fullCollection = {'areas':areaGeomCollection,'lines':lineGeomCollection}
    with open(thisRepo+"report/data/cities/"+str(city['id'])+".json", 'wb') as outfile:
        json.dump(fullCollection, outfile)
    
    

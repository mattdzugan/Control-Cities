import pickle
import numpy as np
import pandas as pd
import xlsxwriter
from jellyfish import jaro_distance
import scipy.cluster.hierarchy
import csv
import json
import ujson

thisRepo = '/home/mattdzugan/Documents/dev/Control Cities/'

interstates = pickle.load(open(thisRepo+"data/interim/InterstatesWithCityIDs.p","rb"))
voronoiResults = pickle.load(open(thisRepo + "data/interim/InterstateVoronoi.p", "rb"))
cities = pd.DataFrame.from_csv(thisRepo+"data/Raw/uscitiesv1.2.csv", index_col=13)


interstateList = []



for idx, interstate in interstates.iterrows():
    #if (idx>10):
    #    break
    print("##############"+str(idx))

    # for tableOfContents JSON object
    thisInterstateForList = {'id': idx, 'text': interstate.Name}
    interstateList.append(thisInterstateForList)
    
    # for main JSON object
    myName = interstate.Name
    myNumber = [int(s) for s in myName.split() if s.isdigit()]
    myNumber = myNumber[0]
    thisInterstateForJSON = {'id': idx, 'LongName': myName, 'ShortName': ('I-'+str(myNumber)), 'Number':myNumber}
    thisInterstateForJSON['direction'] = interstate.Direction

    pathFrame = interstate['Path']
    # go through path, 
    # recording lat lons, 
    # but also keeping list of cities
    jsonPath = []
    citiesWith = []
    citiesAgainst = []
    for jdx, coordinate in pathFrame.iterrows():
        # build the path content        
        mySegmentLon = round(pathFrame['lon'][jdx],5)
        mySegmentLat = round(pathFrame['lat'][jdx],5)
        mySegmentIndx = jdx
        mySegmentID = pathFrame['pointID'][jdx]
        mySegment = {'id':mySegmentID, 'indx':mySegmentIndx, 'lat':mySegmentLat, 'lon':mySegmentLon}
        jsonPath.append(mySegment)
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
                            myStop = leg['StopIndex']
                            myStart = jdx - 1
                            leg['StartIndex'] = myStart
                            leg['length'] = abs(pathFrame['dist'][myStart]-pathFrame['dist'][myStop])
                            legsAgainst.append(leg)
                            inLeg = False
                    else:
                        #start a new leg
                        myCityName = cities.loc[int(cc)].city_ascii
                        leg = {'cityID':cc, 'StopIndex':jdx, 'cityName':myCityName}
                        inLeg = True
                else:
                    if inLeg:
                        # close out the leg
                        myStop = leg['StopIndex']
                        myStart = jdx - 1
                        leg['StartIndex'] = myStart
                        leg['length'] = abs(pathFrame['dist'][myStart]-pathFrame['dist'][myStop])
                        legsAgainst.append(leg)
                        inLeg = False
                    else: 
                        # keep waiting
                        inLeg = False
    
    
     
    # start with the longest leg, assign it the lowest nonOverlapped layer
    legsWith = sorted(legsWith, key=lambda k: k['length'], reverse=True)
    legsAgainst = sorted(legsAgainst, key=lambda k: k['length'], reverse=True)
    assignedWith = []
    assignedAgainst = []
    # # With
    for leg in legsWith:
        a0 = leg['StartIndex']
        a1 = leg['StopIndex']
        # initial condition for "while loop"
        anyOverlaps = True        
        layerToTry = 0
        while anyOverlaps: 
            # start a fresh search with this new layer, assuming no overlaps
            anyOverlaps = False
            layerToTry += 1
            for legToCheck in assignedWith:
                if (legToCheck['layer']==layerToTry):
                    b0 = legToCheck['StartIndex']
                    b1 = legToCheck['StopIndex']
                    if ((b0<=a0)&(b1>=a0)):
                        anyOverlaps = True
                    if ((b1>=a1)&(b0<=a1)):
                        anyOverlaps = True
            if not anyOverlaps:
                leg['layer'] = layerToTry
                leg['length'] = round(leg['length'], 3)
                assignedWith.append(leg)
                break
    # # Against
    for leg in legsAgainst:
        a0 = leg['StartIndex']
        a1 = leg['StopIndex']
        # initial condition for "while loop"
        anyOverlaps = True        
        layerToTry = 0
        while anyOverlaps: 
            # start a fresh search with this new layer, assuming no overlaps
            anyOverlaps = False
            layerToTry += 1
            for legToCheck in assignedAgainst:
                if (legToCheck['layer']==layerToTry):
                    b0 = legToCheck['StartIndex']
                    b1 = legToCheck['StopIndex']
                    if ((b0<=a0)&(b1>=a0)):
                        anyOverlaps = True
                    if ((b1>=a1)&(b0<=a1)):
                        anyOverlaps = True
            if not anyOverlaps:
                leg['layer'] = layerToTry
                leg['length'] = round(leg['length'], 3)
                assignedAgainst.append(leg)
                break
    thisInterstateForJSON['Path'] = jsonPath
    thisInterstateForJSON['Cities'] = {"With":assignedWith, "Against":assignedAgainst}
    with open(thisRepo+"report/data/interstates/"+str(idx)+".json", 'wb') as outfile:
        json.dump(thisInterstateForJSON, outfile)


with open(thisRepo+"report/data/interstateList.json", 'wb') as outfile:
        json.dump(interstateList, outfile)


import pickle
import pandas as pd
import math
import json


thisRepo = '/home/mattdzugan/Documents/dev/Control Cities/'

interstates = pickle.load(open(thisRepo+"data/interim/InterstatesWithCityIDs.p","rb"))
voronoiResults = pickle.load(open(thisRepo + "data/interim/InterstateVoronoi.p", "rb"))
cities = pd.DataFrame.from_csv(thisRepo+"data/Raw/uscitiesv1.2.csv", index_col=13)

km2mi = 0.621371

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

## start the main code
scorecard = pd.DataFrame(columns=['mileage','area','numHighways','farthest'])


for idx, interstate in interstates.iterrows():
    #if (idx>25):
    #   break
    pathFrame = interstate['Path']
    print("##############"+str(idx))
    thisInterstateBookedYet = []
    for jdx, coordinate in pathFrame.iterrows():
        #print(jdx)
        mySegmentLon = pathFrame['lon'][jdx]
        mySegmentLat = pathFrame['lat'][jdx]
        mySegmentLength = pathFrame['segmentLength'][jdx]
        myPointID = pathFrame['pointID'][jdx]
        mySegmentArea   = voronoiResults['Areas'][myPointID].sum()
        for direction in ['destWith', 'destAgainst']:
            if (direction+'_UniqueNameDests') in pathFrame.columns:
                myDestIDs = pathFrame[(direction+'_UniqueNameDests')][jdx] #_consolidatedDestIDs
            else:
                myDestIDs = []
                
            #myDestNames = pathFrame[(direction + '_consolidatedDests')][jdx]
            for ddx in range(len(myDestIDs)):
                myDestID = int(myDestIDs[ddx])
                if myDestID>0:
                    destLat = cities.loc[myDestID].lat
                    destLon = cities.loc[myDestID].lng
                    destDist = greatCircleDistance(mySegmentLon,mySegmentLat,destLon,destLat)
                    if myDestID in scorecard.index:
                        # it's already here
                        newRound = False
                        scorecard.loc[myDestID,'mileage'] += mySegmentLength
                        scorecard.loc[myDestID,'area'] += mySegmentArea
                        if (destDist>scorecard.loc[myDestID,'farthest']):
                            scorecard.loc[myDestID,'farthest'] = destDist                            
                    else:
                        # start it from scratch
                        newRound = True
                        scorecard.loc[myDestID,'mileage'] = mySegmentLength
                        scorecard.loc[myDestID,'area'] = mySegmentArea
                        scorecard.loc[myDestID,'farthest'] = destDist
                    
                    if (myDestID not in thisInterstateBookedYet):
                        thisInterstateBookedYet.append(myDestID)
                        if newRound:
                            # it's already here
                            scorecard.loc[myDestID,'numHighways'] = 1
                        else:
                            # start it from scratch
                            scorecard.loc[myDestID,'numHighways'] += 1
                    #scorecard['name'][myDestID] = myDestNames[ddx]
                    #scorecard.set_value(myDestID, 'name', myDestNames[ddx])


jsonObj = []
for idx, cityData in scorecard.iterrows():
    myid = int(idx)
    myPop = cities.loc[myid].population
    if myPop>0:
        cityJson = {'rnkId': (myid % 1000000)}
        cityJson['rnkName'] = cities.loc[myid].city_ascii
        cityJson['rnkState'] = cities.loc[myid].state_name
        cityJson['rnkPopTxt'] = "{:,}".format(int(myPop))
        cityJson['rnkPop'] = int(round(myPop))
        cityJson['rnkMiles'] = round(cityData['mileage']*km2mi,1)
        cityJson['rnkArea'] = round(cityData['area']*km2mi*km2mi,1)
        cityJson['rnkCount'] = int(cityData['numHighways'])
        cityJson['rnkDist'] = round(cityData['farthest']*km2mi,1)
        # densities
        cityJson['rnkMilesD'] = round(cityData['mileage']*km2mi/myPop*1000000,1)
        cityJson['rnkAreaD'] = round(cityData['area']*km2mi*km2mi/myPop*1000,1)
        cityJson['rnkCountD'] = round(cityData['numHighways']/myPop*1000000,1)
        cityJson['rnkDistD'] = round(cityData['farthest']*km2mi/myPop*1000000,1)
        jsonObj.append(cityJson)


# sort Descending by Miles
jsonObj = sorted(jsonObj, key=lambda k: k['rnkMiles'], reverse=True)
top5Miles = []
for ii in range(5):
    thisCity = jsonObj[ii]
    top5Miles.append(thisCity['rnkId'])
# sort Descending by Area
jsonObj = sorted(jsonObj, key=lambda k: k['rnkArea'], reverse=True)
top5Area= []
for ii in range(5):
    thisCity = jsonObj[ii]
    top5Area.append(thisCity['rnkId'])
# sort Descending by Count
jsonObj = sorted(jsonObj, key=lambda k: k['rnkCount'], reverse=True)
top5Count = []
for ii in range(5):
    thisCity = jsonObj[ii]
    top5Count.append(thisCity['rnkId'])
# sort Descending by Dist
jsonObj = sorted(jsonObj, key=lambda k: k['rnkDist'], reverse=True)
top5Dist= []
for ii in range(5):
    thisCity = jsonObj[ii]
    top5Dist.append(thisCity['rnkId'])
# sort Descending by MilesD
jsonObj = sorted(jsonObj, key=lambda k: k['rnkMilesD'], reverse=True)
top5MilesD = []
for ii in range(5):
    thisCity = jsonObj[ii]
    top5MilesD.append(thisCity['rnkId'])
# sort Descending by AreaD
jsonObj = sorted(jsonObj, key=lambda k: k['rnkAreaD'], reverse=True)
top5AreaD= []
for ii in range(5):
    thisCity = jsonObj[ii]
    top5AreaD.append(thisCity['rnkId'])
# sort Descending by CountD
jsonObj = sorted(jsonObj, key=lambda k: k['rnkCountD'], reverse=True)
top5CountD = []
for ii in range(5):
    thisCity = jsonObj[ii]
    top5CountD.append(thisCity['rnkId'])
# sort Descending by DistD
jsonObj = sorted(jsonObj, key=lambda k: k['rnkDistD'], reverse=True)
top5DistD= []
for ii in range(5):
    thisCity = jsonObj[ii]
    top5DistD.append(thisCity['rnkId'])
winners = { 't5M':top5Miles,   't5A':top5Area,   't5C':top5Count,   't5D':top5Dist,
            't5MD':top5MilesD, 't5AD':top5AreaD, 't5CD':top5CountD, 't5DD':top5DistD
           }



# sort Descending by pop
jsonObj = sorted(jsonObj, key=lambda k: k['rnkPop'], reverse=True)
jsonStruct = {'list':jsonObj, 'winners':winners}
with open(thisRepo+"report/data/sortableList.json", 'wb') as outfile:
        json.dump(jsonStruct, outfile)
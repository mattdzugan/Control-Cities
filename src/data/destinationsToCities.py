from __future__ import print_function
import pickle
import math as math
import numpy as np
import pandas as pd
from jellyfish import jaro_distance

import os.path
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt


thisRepo = '/home/mattdzugan/Documents/dev/Control Cities/'
manualHelper = open(thisRepo+'data/interim/manualHelper.tsv', 'w')
manualHelp = pd.DataFrame.from_csv(thisRepo+'data/interim/manualHelped.tsv', sep='\t', index_col=False)
# UID, InterstateName, Number, PickleIndex, thisOrigin, thisDestin, theseWayps, startsForward, tfparam1, tfparam2
interstates = pickle.load(open(thisRepo+"data/interim/InterstatesWithDestsAndManual.p","rb"))
cities = pd.DataFrame.from_csv(thisRepo+"data/Raw/uscitiesv1.2.csv", index_col=13)


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

def ismember(A, B):
    return [ np.sum(a == B) for a in A ]
# writer = pd.ExcelWriter(thisRepo+"data/interim/InterstatesWithDests.xlsx")
# for idx, interstate in interstates.iterrows():
#     #print(interstate.Name)
#     pathFrame = interstate['Path']
#     if (idx<=10):
#         print(pathFrame)
#         pathFrame.to_excel(writer,interstate.Name)
def wordSimilarity(vector,word):
    v = vector.values
    N = v.shape[0]
    z = np.zeros((N, 1), dtype=bool)
    for ii in range(N):
        try:
            z[ii] = jaro_distance(unicode(v[ii]), word) > 0.85
        except:
            z[ii] = False
    return z


def cityCloseness(vectorlat,vectorlon,lat,lon):
    vlats = vectorlat.values
    vlons = vectorlon.values
    N = vlats.shape[0]
    z = np.zeros((N, 1), dtype=bool)
    for ii in range(N):
        try:
            z[ii] = greatCircleDistance(vlons[ii],vlats[ii],lon,lat)<50
        except:
            z[ii] = False
    return z


pointID = 0
for idx, interstate in interstates.iterrows():
    print(interstate.Name)
    print(str(idx)+"\t"+interstate.Name+"\t0\t0\t0\t0\t0", file=manualHelper)
    pathFrame = interstate['Path']
    
    thisInterstatesHelp = manualHelp.loc[manualHelp['IntID']==idx]
    
    
    for jdx, coordinate in pathFrame.iterrows():
        pathFrame.set_value(jdx, 'pointID', pointID)
        pointID = pointID + 1
        # determine size of this line segment
        if (jdx==0):
            seg = pathFrame['dist'][1]/2
        elif (jdx==(pathFrame.shape[0]-1)):
            seg = (pathFrame['dist'][jdx] - pathFrame['dist'][jdx - 1]) / 2
        else:
            seg = (((pathFrame['dist'][jdx + 1] - pathFrame['dist'][jdx]) / 2) +
                  ((pathFrame['dist'][jdx] - pathFrame['dist'][jdx - 1]) / 2))
        pathFrame.set_value(jdx, 'segmentLength', seg)
        
        

    for direction in ['destWith', 'destAgainst']:
        thisRoutesHelp = thisInterstatesHelp.loc[thisInterstatesHelp['WithAgainst']==direction]
        #print(direction)
        lent = lambda t: t.shape
        vv = np.vectorize(lent)
        #vvv = vv(pathFrame[direction].values)
        vvv = np.array(map(np.size,pathFrame[direction].values))
        vvv = vvv>0
        if (vvv.sum()==0):
            print()
            # no data for this direction
        else:
            DestinationList = []
            for jdx, coordinate in pathFrame.iterrows():
                theseDests = coordinate[direction]
                numDest = theseDests.shape[0]/2
                if (numDest>0):
                    #print("---")
                    #print(numDest)
                    #print(coordinate[direction])
                    for kk in range(numDest):
                        destName = theseDests[kk]
                        destCount = theseDests[kk+numDest]
                        #print(destName+" at a total of "+str(destCount)+" times.")
                        for ll in range(int(destCount)):
                            DestinationList.append(destName)
            #print(DestinationList)
            unq, unq_idx, unq_cnt = np.unique(DestinationList, return_inverse=True, return_counts=True)
            if (vvv.sum()>1):
                DestinationList = unq[unq_cnt>1] #just changed from 1 to 0
            else:
                DestinationList = unq[unq_cnt>0]
            #vvv[unq_idx[unq_cnt==1]]=False


            #print(DestinationList)
            for jdx, coordinate in pathFrame.iterrows():
                theseDests = coordinate[direction]
                theseApprovedDests = []
                numDest = theseDests.shape[0]/2
                if (numDest>0):
                    for kk in range(numDest):
                        destName = theseDests[kk]
                        if ismember(destName, DestinationList):
                            theseApprovedDests.append(destName)
                #print(theseApprovedDests)
                pathFrame.set_value(jdx,direction,np.array(theseApprovedDests))



            # determine closest  non-blank
            distVec = pathFrame['dist'].values
            hasDests = 1*(vvv) #convert to 0,1 ints
            cumDests = np.cumsum(hasDests)
            wheres = np.where(hasDests)[0]
            xWheres = np.hstack((wheres[0],wheres))

            distVec_rev = distVec[::-1]
            cumDests_rev = np.cumsum(hasDests[::-1])
            wheres_rev = np.where(hasDests[::-1])[0]
            xWheres_rev = np.hstack((wheres_rev[0],wheres_rev))

            IndOfRecentPast = xWheres[cumDests]
            DistToPast = np.absolute(distVec-distVec[IndOfRecentPast])

            IndOfUpcomingNext = xWheres_rev[cumDests_rev]
            DistToNext = np.absolute(distVec_rev-distVec_rev[IndOfUpcomingNext])
            DistToNext = DistToNext[::-1]
            IndOfUpcomingNext = (distVec.shape[0]-1) - IndOfUpcomingNext[::-1]

            #print DistToPast
            #print DistToNext
            for jdx, coordinate in pathFrame.iterrows():
                theseDests = coordinate[direction]
                numDest = theseDests.shape[0]
                if (numDest==0):
                    pastDests = pathFrame[direction].values[IndOfRecentPast[jdx]]
                    nextDests = pathFrame[direction].values[IndOfUpcomingNext[jdx]]
                    # if past==next for a non-end-point.... do it no matter what                    
                    if ((str(pastDests)==str(nextDests))&(not(IndOfRecentPast[jdx]==IndOfRecentPast[0]))&(not(IndOfUpcomingNext[jdx]==IndOfUpcomingNext[pathFrame.shape[0]-1]))):
                        theseDests = pathFrame[direction].values[IndOfRecentPast[jdx]]                    
                    # else, only do it within 50 miles (80.4672 km)
                    if (DistToPast[jdx]<DistToNext[jdx]):
                        if (DistToPast[jdx]<80.467):
                            theseDests = pathFrame[direction].values[IndOfRecentPast[jdx]]
                            #theseDests = IndOfRecentPast[jdx]
                    else:
                        if (DistToNext[jdx]<80.467):
                            theseDests = pathFrame[direction].values[IndOfUpcomingNext[jdx]]
                        #theseDests = IndOfUpcomingNext[jdx]
                pathFrame.set_value(jdx,direction,theseDests)
                #print(theseDests)

            # for each of the desinations in this DestinationList give it a unique name
            destinationFrame = pd.DataFrame({'UniqueName': np.array(DestinationList)}, index=np.array(DestinationList))
            gotTheFirstOne = 0
            for jdx, destination in destinationFrame.iterrows():
                thisDestName = destination['UniqueName']
                for kdx, coordinate in pathFrame.iterrows():
                    theseDests = coordinate[direction]
                    if (thisDestName in theseDests):
                        rawLat = coordinate['lat']
                        rawLon = coordinate['lon']
                        if (direction is 'destAgainst'):
                            break
                somewhatNearby = cities.loc[(abs(cities['lat']-rawLat) < 3) & (abs(cities['lng']-rawLon) < 3)]
                similarName = somewhatNearby[wordSimilarity(somewhatNearby['city'], unicode(thisDestName))]
                nearby = similarName[cityCloseness(similarName['lng'],similarName['lat'],rawLon,rawLat)]
                # determine all the cities that are within 3 degs lat/lon of this "last point"
                # determine all the cities from that list who have a jaro distance >0.8
                # determine all cities who are <100km from these
                thisDestUniqueName = '0'
                if (nearby.shape[0]==1):
                    thisDestUniqueName = str(nearby.index[0])
                    #print(""+thisDestName+"-->"+nearby['city'].values[0])
                else:
                    thisSolution = thisRoutesHelp.loc[thisRoutesHelp['Name']==thisDestName]
                    if (thisSolution.shape[0]==1):
                        newID = thisSolution['NewID'].values[0]
                        thisDestUniqueName = str(int(newID))
                        #
                    else:
                        print("WTF")
                    try:
                        print(str(idx) + "\t" + thisDestName.encode('utf-8') + "\t" + str(rawLat) + "\t"+str(rawLon) + "\t" + direction + "\t" + interstate['Direction'], file=manualHelper)
                    except:
                        print(str(idx) + "\t" + "NAH" + "\t" + str(rawLat) + "\t" + str(
                            rawLon) + "\t" + direction + "\t" + interstate['Direction']+"\t0", file=manualHelper)

                    #if (nearby.shape[0]==0):
                        #print("      ...i got nothing")
                    #else:
                        #print("      ...it's either: " + str(nearby['city'].values))
                    #thisDestUniqueName = '-999'
                destinationFrame.set_value(thisDestName,'UniqueName',thisDestUniqueName)
                #print(thisDestName+'--->'+thisDestUniqueName)
            #print ('#############################################################')
            #print destinationFrame


            if True: # bring this back after i implement the manual fix
                arrayOfUniqueDests = []
                for jdx, coordinate in pathFrame.iterrows():
                    theseDests = coordinate[direction]
                    theseUniqueDestNames = []
                    numDest = theseDests.shape[0]
                    for thisDest in theseDests:
                        if (thisDest in destinationFrame.index):
                            thisDestUniqueName = destinationFrame.get_value(thisDest,'UniqueName')
                            theseUniqueDestNames.append(thisDestUniqueName)
                    arrayOfUniqueDests.append(theseUniqueDestNames)
                try:
                    newFirst = arrayOfUniqueDests[0]
                    newFirst.append('0')
                    arrayOfUniqueDests[0] = newFirst
                    pathFrame.loc[:,(direction+'_UniqueNameDests')] = np.array(arrayOfUniqueDests)
                except:
                    print('weird stuff with '+interstate.Name+' '+direction)


    interstates.set_value(idx,'Path',pathFrame)
    #if (idx>=2):
    #    break




pickle.dump(interstates,open(thisRepo+"data/interim/InterstatesWithCityIDs.p","wb"))

writer = pd.ExcelWriter(thisRepo+"data/interim/InterstatesWithCityIDs.xlsx")
for idx, interstate in interstates.iterrows():
    #print(interstate.Name)
    pathFrame = interstate['Path']
    if ((idx<=30)|(idx==166)):
        #print(pathFrame)
        sheetName = interstate.Name
        pathFrame.to_excel(writer,sheetName[:30])




import pickle
import math as math
import numpy as np
import pandas as pd
import os.path
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt

thisRepo = '/home/mattdzugan/Documents/dev/Control Cities/'

# UID, InterstateName, Number, PickleIndex, thisOrigin, thisDestin, theseWayps, startsForward, tfparam1, tfparam2
interstates = pickle.load(open(thisRepo+"data/interim/Interstates.p","rb"))
TaskList    = pickle.load(open(thisRepo+"data/interim/TaskList.p","rb"))


################################################################################
################################################################################
###                         Useful Functions                                 ###
################################################################################
################################################################################
def getClosestPointIndex(latList, lonList, quereyLat, quereyLon):
    latDist = abs(latList-quereyLat)
    lonDist = abs(lonList-quereyLon)
    dists = np.hypot(latDist,lonDist*math.cos(math.radians(quereyLat)))
    return np.argmin(dists)


################################################################################
################################################################################
###                     Tie Results to Interstates                           ###
################################################################################
################################################################################
# load "interstate" frame and a column (next to "lat" and "lon" for destWith and destAgainst)
interstates['Path'] = ""
for idx, interstate in interstates.iterrows():
    #print(interstate.Name)
    pathFrame = pd.DataFrame({"lat":interstate.Lats,   "lon":interstate.Lons,   "dist":interstate.Dist})
    pathFrame['destWith'] = np.empty((len(pathFrame), 0)).tolist()
    pathFrame['destAgainst'] = np.empty((len(pathFrame), 0)).tolist()
    interstates.set_value(idx,'Path',pathFrame)
    plt.plot(pathFrame['lon'].values,pathFrame['lat'].values,'k')


# for idx, task in TaskList.iterrows():
#     thisInterstateName = task.InterstateName
#     thisNumber = task.Number
#     thisUID = task.UID
#     taskFileDir = thisRepo+'data/interim/directions/I-'+str(thisNumber)+'__'+str(thisInterstateName)+'/'
#     taskFileName = 'UID_'+str(thisUID)+'.tsv'
#     taskFilePath = taskFileDir+taskFileName
#     interstateIdx = task.PickleIndex
#     print(idx)
#     if ((idx>5000)&(idx<5100)):
#         if os.path.exists(taskFilePath):
#             gmapsData = pd.read_csv(taskFilePath, sep="\t", encoding='utf-8')
#             interstatePath = interstates.loc[interstateIdx,'Path']
#             pathLat = interstatePath['lat'].values
#             pathLon = interstatePath['lon'].values
#             for ii, result in gmapsData.iterrows():
#                 ind = getClosestPointIndex(pathLat, pathLon, result.lat, result.lon)
#                 plt.scatter(result.lon, result.lat, c='r')
#                 plt.scatter(pathLon[ind], pathLat[ind], c='g')
# plt.show()





# for each Task
# # add a duple to destWIth (or destAgainst) that has the "DestinationName" and the "DestinationCount"
for idx, task in TaskList.iterrows():
    thisInterstateName = task.InterstateName
    thisNumber = task.Number
    thisUID = task.UID
    taskFileDir = thisRepo+'data/interim/directions/I-'+str(thisNumber)+'__'+str(thisInterstateName)+'/'
    taskFileName = 'UID_'+str(thisUID)+'.tsv'
    taskFilePath = taskFileDir+taskFileName
    interstateIdx = task.PickleIndex


    if os.path.exists(taskFilePath):
        gmapsData = pd.read_csv(taskFilePath, sep="\t", encoding='utf-8')
        interstatePath = interstates.loc[interstateIdx,'Path']
        #interstateLatLons = interstatePath[['lat','lon']].value
        #print(interstateLatLons)
        pathLat = interstatePath['lat'].values
        pathLon = interstatePath['lon'].values
        #numCoords = len(interstatePath.index)

        for ii, result in gmapsData.iterrows():
            ind = getClosestPointIndex(pathLat, pathLon, result.lat, result.lon)

            if (result['dir']==1):
                thisDestList = interstatePath.loc[ind,'destWith']
            else:
                thisDestList = interstatePath.loc[ind,'destAgainst']


            resultList = result['str']
            resultVec = resultList.split("     ")
            for destination in resultVec:
                thisDestList.append(destination)
                #print(thisDestList)
                #if (destination in thisDestList):
                #    thisDestList[destination] = 1+thisDestList[destination]
                #else:
                #    thisDestList[destination] = 1

            if (result['dir']==1):
                interstatePath.set_value(ind,'destWith',thisDestList)
            else:
                interstatePath.set_value(ind,'destAgainst',thisDestList)
        interstates.set_value(interstateIdx,'Path',interstatePath)

    print(thisUID)

for idx, interstate in interstates.iterrows():
    #print(interstate.Name)
    pathFrame = interstate['Path']

    for jdx, coordinate in pathFrame.iterrows():
        destNames, destCounts = np.unique(coordinate['destWith'], return_counts=True)
        pathFrame.set_value(jdx,'destWith',np.concatenate([destNames,destCounts]))
        destNames, destCounts = np.unique(coordinate['destAgainst'], return_counts=True)
        pathFrame.set_value(jdx,'destAgainst',np.concatenate([destNames,destCounts]))

    #print(pathFrame)
    interstates.set_value(idx,'Path',pathFrame)

################################################################################
################################################################################
###                         Filter out the Duds                              ###
################################################################################
################################################################################
# get rid of "Ave" or "Rd" or "St" or "Ln" or "Hwy" or "Rte"
# get rid of anything with 10% of the max's appearances


################################################################################
################################################################################
###                          Store the Result                                ###
################################################################################
################################################################################
pickle.dump(interstates,open(thisRepo+"data/interim/InterstatesWithDests.p","wb"))

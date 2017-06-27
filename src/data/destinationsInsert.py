from __future__ import print_function
import pickle
import numpy as np
import pandas as pd
import math



thisRepo = '/home/mattdzugan/Documents/dev/Control Cities/'
interstates = pickle.load(open(thisRepo+"data/interim/InterstatesWithDests.p","rb"))




################################################################################
################################################################################
###                         Useful Functions                                 ###
################################################################################
################################################################################
def getClosestPointIndex(lonList, quereyLon):
    lonDist = abs(lonList-quereyLon)
    dists = np.abs(lonDist)
    return np.argmin(dists)




## Yes this process in manual... sue me
iterations = [  {"ind":50,  "file":"I10",  "doWith":True,  "doAgainst":True},
                {"ind":169, "file":"I40",  "doWith":True,  "doAgainst":True},
                {"ind":140, "file":"I70E", "doWith":True,  "doAgainst":False},
                {"ind":140, "file":"I70W", "doWith":False, "doAgainst":True},
                {"ind":166, "file":"I80",  "doWith":True,  "doAgainst":True},
                {"ind":3,   "file":"I90",  "doWith":True,  "doAgainst":True} ]

for iteration in iterations:
    I = interstates.loc[iteration['ind']]
    pathFrame = I['Path']
    lonsVec = I['Lons']
    latsVec = I['Lats']
    helper = pd.DataFrame.from_csv(thisRepo+"data/Raw/manual/"+iteration['file']+".csv", index_col=0)
    cityInds = []
    for idx, city in helper.iterrows():
        cityName = city['City']
        cityLon = city['Lon']
        cityInd = getClosestPointIndex(lonsVec, cityLon)
        cityLat = latsVec[cityInd]
        cityInd10MilesEast = getClosestPointIndex(lonsVec, cityLon+16.09/(111.0*math.cos(cityLat/180*3.1415)))
        cityInd10MilesWest = getClosestPointIndex(lonsVec, cityLon-16.09/(111.0*math.cos(cityLat/180*3.1415)))
        cityInds.append({'name':cityName, 'ind':cityInd, 'ind10ME':cityInd10MilesEast, 'ind10MW':cityInd10MilesWest})
    N = len(cityInds)
    for ii in range(N-1):
        eastOfA = cityInds[ii]['ind10ME']
        westOfB = cityInds[ii+1]['ind10MW']
        # WITH
        if iteration['doWith']:
            destsWith = pathFrame.loc[eastOfA:westOfB,'destWith'].values
            allEmptyWith = all(np.array(map(np.size,destsWith))==0)
            if ((destsWith.size>=3)&(allEmptyWith)):
                pathFrame.set_value(eastOfA,'destWith',np.array(['qwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjklzxcvbnm','20']))
                pathFrame.set_value(eastOfA+1,'destWith',np.array([cityInds[ii+1]['name'],'20']))
                pathFrame.set_value(westOfB-1,'destWith',np.array([cityInds[ii+1]['name'],'20']))
                pathFrame.set_value(westOfB,'destWith',np.array(['qwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjklzxcvbnm','20']))
        # AGAINST
        if iteration['doAgainst']:
            destsAgainst = pathFrame.loc[eastOfA:westOfB,'destAgainst'].values
            allEmptyAgainst = all(np.array(map(np.size,destsAgainst))==0)
            if ((destsAgainst.size>=3)&(allEmptyAgainst)):
                pathFrame.set_value(eastOfA,'destAgainst',np.array(['qwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjklzxcvbnm','20']))
                pathFrame.set_value(eastOfA+1,'destAgainst',np.array([cityInds[ii]['name'],'20']))
                pathFrame.set_value(westOfB-1,'destAgainst',np.array([cityInds[ii]['name'],'20']))
                pathFrame.set_value(westOfB,'destAgainst',np.array(['qwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjklzxcvbnm','20']))

pickle.dump(interstates,open(thisRepo+"data/interim/InterstatesWithDestsAndManual.p","wb"))





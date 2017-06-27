from bs4 import BeautifulSoup
import os
import pickle
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import math as math
import string
from unidecode import unidecode
import collections
import numpy as np
import pandas as pd

thisRepo = '/home/mattdzugan/Documents/dev/Control Cities/'


################################################################################
################################################################################
###             Find and read all files from the Wikipedia scrape            ###
################################################################################
################################################################################

InterstateData2Frame = []
## Find all files in the directory
RoutesPerInterstate = [];
for file in os.listdir(thisRepo + 'data/Raw/Wikipedia/'):
    if file.endswith(".kml"):
        #print("")
        #print((file))

        # read the file
        f = open((thisRepo + 'data/Raw/Wikipedia/'+file),'r')
        filecontents = f.read()
        mySoup = BeautifulSoup(filecontents, "lxml")
        coordinateSets = mySoup.find_all("coordinates")
        RoutesPerInterstate.append(len(coordinateSets))
        #print(len(coordinateSets))


        # go look route by route
        #Routes = []
        RoutesData2Frame = []
        for thisRoute in coordinateSets:

            # go determine the name
            myRouteName=file
            for parent in thisRoute.parents:
                if (parent.name == "placemark"):
                    #print("-----"+parent.name)
                    routeName = (parent.find_all("name"))
                    if (len(routeName)>0):
                        thisRouteName = routeName[0].string
                        myRouteName=unidecode(thisRouteName)
                    else:
                        myRouteName=file
                    break
            #print(myRouteName)

            # go get the path
            coordinateString = thisRoute.string
            coordinateList = string.split(coordinateString, sep=None)
            LatList = []
            LonList = []
            #print("Num Coords   "+str(len(coordinateList)))
            for coord in coordinateList:
                theseParts = string.split(coord, sep=',')
                try:
                    thisLon = float(theseParts[0])
                    thisLat = float(theseParts[1])
                    LonList.append( thisLon )
                    LatList.append( thisLat )
                except:
                    print("FAILED coord string:    "+coord+" on file: " +file)
            #myRouteData = RouteData(lat=LatList, lon=LonList, dist=-1, neControlCity=-1, swControlCity=-1, localPop=-1,)
            #myRouteDataDF = pd.DataFrame({  'Lat':np.array(LatList, dtype='float32'),
            #                                'Lon':np.array(LonList, dtype='float32')})
            # combine to a "Route"
            #myRoute = Route(name=myRouteName,length=-1,northEastTerminal=-1,southWestTerminal=-1,routeData=myRouteData)
            #myRouteDF =  pd.DataFrame({     'name':myRouteName,
            #                                'data':myRouteDataDF })
            #Routes.append(myRoute)
            RoutesData2Frame.append( {  'Name':myRouteName,
                                        'Lat':np.array(LatList, dtype='float32'),
                                        'Lon':np.array(LonList, dtype='float32')} )
        #thisInterstate = Interstate(title=myRouteName, routes=Routes)
        RoutesDataFrame = pd.DataFrame(RoutesData2Frame)
        InterstateData2Frame.append({"title":file, "routes":RoutesDataFrame})
        #Interstates.append(thisInterstate)
InterstatesDataFrame = pd.DataFrame(InterstateData2Frame)

#plt.hist(RoutesPerInterstate, [0,1,2,3,4,5,6,7,8,9,10,50], facecolor='green', alpha=0.75)
#plt.show()
print("Ok, so I've gathered: "+str(InterstatesDataFrame.shape[0])+" Interstates, each with a couple routes.  Time to delete simple one-point-routes")


################################################################################
################################################################################
###             From each interstate, remove sub-routes of size 1            ###
################################################################################
################################################################################

for index, interstate in InterstatesDataFrame.iterrows():
    numRoutes = interstate['routes'].shape[0]
    if numRoutes>1:
        myRoutes = interstate.routes
        #for r_index, route in myRoutes.iterrows():
        #    print("length of this route is: "+str(route.Lat.shape[0]))
        vfun = np.vectorize(len)
        routeLengths = (vfun(myRoutes.Lat))
        #print(routeLengths)
        myNewRoutes = myRoutes[ routeLengths>1 ]
        myNewRoutes = myNewRoutes.reset_index()
        interstate.routes = myNewRoutes

print("Ok, so I've still got "+str(InterstatesDataFrame.shape[0])+" Interstates, each with a couple routes.  Time to delete some with keywords")


################################################################################
################################################################################
###          From each interstate, remove sub-routes with bad titles         ###
################################################################################
################################################################################

for index, interstate in InterstatesDataFrame.iterrows():
    myRoutes = interstate.routes
    numRoutes = interstate['routes'].shape[0]
    keepThisRoute = np.ones((numRoutes))
    for r_index, route in myRoutes.iterrows():
        myName =route.Name
        keepThisRoute[r_index] *= ("spur" not in myName.lower())
        keepThisRoute[r_index] *= ("proposed" not in myName.lower())
        keepThisRoute[r_index] *= ("future" not in myName.lower())
        keepThisRoute[r_index] *= ("planned" not in myName.lower())
        keepThisRoute[r_index] *= ("planning" not in myName.lower())
        #if (keepThisRoute[r_index] != 1):
        #    print (myName)
    myNewRoutes = myRoutes[ (keepThisRoute==1) ]
    interstate.routes = myNewRoutes


################################################################################
################################################################################
###             Flatten multi-route interstates into single pieces           ###
################################################################################
################################################################################

FlattenedInterstates = []
#
for index, interstate in InterstatesDataFrame.iterrows():
    myRoutes = interstate.routes
    numRoutes = interstate['routes'].shape[0]
    theName = interstate['title'][:-4]
    if numRoutes>1:
        # I apologize for this hack, but the KML data on wikipedia isn't perfect
        # so i have to do this "manually"
        if (theName == 'Interstate 530 (Arkansas)'):
            # keep first route only
            theRoute = myRoutes.iloc[0]
            FlattenedInterstates.append({   'Name':theName,
                                            'Lats':np.array(theRoute.Lat, dtype='float32'),
                                            'Lons':np.array(theRoute.Lon, dtype='float32')} )

        elif (theName == 'Interstate 895 (Maryland)'):
            # keep first route only
            theRoute = myRoutes.iloc[0]
            FlattenedInterstates.append({   'Name':theName,
                                            'Lats':np.array(theRoute.Lat, dtype='float32'),
                                            'Lons':np.array(theRoute.Lon, dtype='float32')} )

        elif (theName == 'Interstate 86 (Pennsylvania-New York)'):
            # keep first route only
            theRoute = myRoutes.iloc[0]
            FlattenedInterstates.append({   'Name':theName,
                                            'Lats':np.array(theRoute.Lat, dtype='float32'),
                                            'Lons':np.array(theRoute.Lon, dtype='float32')} )

        elif (theName == 'Interstate 84 (Oregon-Utah)'):
            # stitch all routes together
            latlist = np.array([])
            lonlist = np.array([])
            for r_index, route in myRoutes.iterrows():
                if (r_index==1): # yeah this piece is backwards
                    latlist = np.append(latlist,np.flipud(route['Lat']))
                    lonlist = np.append(lonlist,np.flipud(route['Lon']))
                else:
                    latlist = np.append(latlist,route['Lat'])
                    lonlist = np.append(lonlist,route['Lon'])
            FlattenedInterstates.append({   'Name':theName,
                                            'Lats':np.array(latlist, dtype='float32'),
                                            'Lons':np.array(lonlist, dtype='float32')} )

        elif (theName == 'Interstate 695 (Maryland)'):
            # keep first route only
            theRoute = myRoutes.iloc[0]
            FlattenedInterstates.append({   'Name':theName,
                                            'Lats':np.array(theRoute.Lat, dtype='float32'),
                                            'Lons':np.array(theRoute.Lon, dtype='float32')} )

        elif (theName == 'Interstate 8'):
            # stitch together routes 0,2,3,4,6
            latlist = np.array([])
            lonlist = np.array([])
            for r_index, route in myRoutes.iterrows():
                if (r_index==2): # yeah this piece is backwards
                    latlist = np.append(latlist,np.flipud(route['Lat']))
                    lonlist = np.append(lonlist,np.flipud(route['Lon']))
                elif ((r_index==0)|(r_index==3)|(r_index==4)|(r_index==6)):
                    latlist = np.append(latlist,route['Lat'])
                    lonlist = np.append(lonlist,route['Lon'])
            FlattenedInterstates.append({   'Name':theName,
                                            'Lats':np.array(latlist, dtype='float32'),
                                            'Lons':np.array(lonlist, dtype='float32')} )

        elif (theName == 'Interstate 95'):
            # separate and use names {Interstate 95 (Southern Segment), Interstate 95 (Northern Segment)}
            theRoute = myRoutes.iloc[0]
            FlattenedInterstates.append({   'Name':'Interstate 95 (Southern Segment)',
                                            'Lats':np.array(theRoute.Lat, dtype='float32'),
                                            'Lons':np.array(theRoute.Lon, dtype='float32')} )
            theRoute = myRoutes.iloc[1]
            FlattenedInterstates.append({   'Name':'Interstate 95 (Northern Segment)',
                                            'Lats':np.array(theRoute.Lat, dtype='float32'),
                                            'Lons':np.array(theRoute.Lon, dtype='float32')} )

        elif (theName == 'Interstate 315 (Montana)'):
            # keep first route only
            theRoute = myRoutes.iloc[0]
            FlattenedInterstates.append({   'Name':theName,
                                            'Lats':np.array(theRoute.Lat, dtype='float32'),
                                            'Lons':np.array(theRoute.Lon, dtype='float32')} )

        elif (theName == 'Interstate 265 (Kentucky)'):
            # keep first route only
            theRoute = myRoutes.iloc[0]
            FlattenedInterstates.append({   'Name':theName,
                                            'Lats':np.array(theRoute.Lat, dtype='float32'),
                                            'Lons':np.array(theRoute.Lon, dtype='float32')} )

        elif (theName == 'Interstate 480 (Ohio)'):
            # keep first route only
            theRoute = myRoutes.iloc[0]
            FlattenedInterstates.append({   'Name':theName,
                                            'Lats':np.array(theRoute.Lat, dtype='float32'),
                                            'Lons':np.array(theRoute.Lon, dtype='float32')} )

        elif (theName == 'Interstate 540 (North Carolina)'):
            # keep first route only
            theRoute = myRoutes.iloc[0]
            FlattenedInterstates.append({   'Name':theName,
                                            'Lats':np.array(theRoute.Lat, dtype='float32'),
                                            'Lons':np.array(theRoute.Lon, dtype='float32')} )

        elif (theName == 'Interstate 99'):
            # separate and use names {Interstate 99 (Pennsylvania), Interstate 99 (New York)}
            theRoute = myRoutes.iloc[0]
            FlattenedInterstates.append({   'Name':'Interstate 99 (Pennsylvania)',
                                            'Lats':np.array(theRoute.Lat, dtype='float32'),
                                            'Lons':np.array(theRoute.Lon, dtype='float32')} )
            theRoute = myRoutes.iloc[1]
            FlattenedInterstates.append({   'Name':'Interstate 99 (New York)',
                                            'Lats':np.array(theRoute.Lat, dtype='float32'),
                                            'Lons':np.array(theRoute.Lon, dtype='float32')} )

        elif (theName == 'Interstate 276 (Pennsylvania)'):
            # stitch all routes together
            latlist = np.array([])
            lonlist = np.array([])
            for r_index, route in myRoutes.iterrows():
                latlist = np.append(latlist,route['Lat'])
                lonlist = np.append(lonlist,route['Lon'])
            FlattenedInterstates.append({   'Name':theName,
                                            'Lats':np.array(latlist, dtype='float32'),
                                            'Lons':np.array(lonlist, dtype='float32')} )

        elif (theName == 'Interstate 710'):
            # keep first route only
            theRoute = myRoutes.iloc[0]
            FlattenedInterstates.append({   'Name':theName,
                                            'Lats':np.array(theRoute.Lat, dtype='float32'),
                                            'Lons':np.array(theRoute.Lon, dtype='float32')} )

        elif (theName == 'Interstate 105 (Oregon)'):
            # keep first route only
            theRoute = myRoutes.iloc[0]
            FlattenedInterstates.append({   'Name':theName,
                                            'Lats':np.array(theRoute.Lat, dtype='float32'),
                                            'Lons':np.array(theRoute.Lon, dtype='float32')} )

        elif (theName == 'Interstate 759 (Alabama)'):
            # keep first route only
            theRoute = myRoutes.iloc[0]
            FlattenedInterstates.append({   'Name':theName,
                                            'Lats':np.array(theRoute.Lat, dtype='float32'),
                                            'Lons':np.array(theRoute.Lon, dtype='float32')} )
        elif (theName == 'Interstate 74'):
            # separate routes and use names {Interstate 74, Interstate 74 (Western North Carolina Segment), Interstate 74 (Central North Carolina Segment), Interstate 74 (Eastern North Carolina Segment)}
            theRoute = myRoutes.iloc[0]
            FlattenedInterstates.append({   'Name':'Interstate 74',
                                            'Lats':np.array(theRoute.Lat, dtype='float32'),
                                            'Lons':np.array(theRoute.Lon, dtype='float32')} )
            theRoute = myRoutes.iloc[1]
            FlattenedInterstates.append({   'Name':'Interstate 74 (Western North Carolina Segment)',
                                            'Lats':np.array(theRoute.Lat, dtype='float32'),
                                            'Lons':np.array(theRoute.Lon, dtype='float32')} )
            theRoute = myRoutes.iloc[2]
            FlattenedInterstates.append({   'Name':'Interstate 74 (Central North Carolina Segment)',
                                            'Lats':np.array(theRoute.Lat, dtype='float32'),
                                            'Lons':np.array(theRoute.Lon, dtype='float32')} )
            theRoute = myRoutes.iloc[3]
            FlattenedInterstates.append({   'Name':'Interstate 74 (Eastern North Carolina Segment)',
                                            'Lats':np.array(theRoute.Lat, dtype='float32'),
                                            'Lons':np.array(theRoute.Lon, dtype='float32')} )

        elif (theName == 'Interstate 94'):
            # stitch all routes together in a weird order (0 --> 6 --> 2 --> 3 --> 1 --> 4 --> 5)
            latlist = np.array([])
            lonlist = np.array([])
            theRoute = myRoutes.iloc[0]
            latlist = np.append(latlist,(theRoute.Lat))
            lonlist = np.append(lonlist,(theRoute.Lon))
            theRoute = myRoutes.iloc[6]
            latlist = np.append(latlist,(theRoute.Lat))
            lonlist = np.append(lonlist,(theRoute.Lon))
            theRoute = myRoutes.iloc[2]
            latlist = np.append(latlist,(theRoute.Lat))
            lonlist = np.append(lonlist,(theRoute.Lon))
            theRoute = myRoutes.iloc[3]
            latlist = np.append(latlist,(theRoute.Lat))
            lonlist = np.append(lonlist,(theRoute.Lon))
            theRoute = myRoutes.iloc[1]
            latlist = np.append(latlist,np.flipud(theRoute.Lat))
            lonlist = np.append(lonlist,np.flipud(theRoute.Lon))
            theRoute = myRoutes.iloc[4]
            latlist = np.append(latlist,(theRoute.Lat))
            lonlist = np.append(lonlist,(theRoute.Lon))
            theRoute = myRoutes.iloc[5]
            latlist = np.append(latlist,(theRoute.Lat))
            lonlist = np.append(lonlist,(theRoute.Lon))
            FlattenedInterstates.append({   'Name':theName,
                                            'Lats':np.array(latlist, dtype='float32'),
                                            'Lons':np.array(lonlist, dtype='float32')} )

        elif (theName == 'Interstate 676 (New Jersey)'):
            # keep first route only
            theRoute = myRoutes.iloc[0]
            FlattenedInterstates.append({   'Name':theName,
                                            'Lats':np.array(theRoute.Lat, dtype='float32'),
                                            'Lons':np.array(theRoute.Lon, dtype='float32')} )

        elif (theName == 'Interstate 49'):
            # separate routes and use names {Interstate 49 (Louisiana-South), Interstate 49 (Louisiana-North), Interstate 49 (Arkansas-South), Interstate 49 (Arkansas-North), Interstate 49 (Missouri)}
            theRoute = myRoutes.iloc[0]
            FlattenedInterstates.append({   'Name':'Interstate 49 (Lousiana-South Segment',
                                            'Lats':np.array(theRoute.Lat, dtype='float32'),
                                            'Lons':np.array(theRoute.Lon, dtype='float32')} )
            theRoute = myRoutes.iloc[1]
            FlattenedInterstates.append({   'Name':'Interstate 49 (Lousiana-North Segment)',
                                            'Lats':np.array(theRoute.Lat, dtype='float32'),
                                            'Lons':np.array(theRoute.Lon, dtype='float32')} )
            theRoute = myRoutes.iloc[2]
            FlattenedInterstates.append({   'Name':'Interstate 49 (Arkansas-South Segment)',
                                            'Lats':np.array(theRoute.Lat, dtype='float32'),
                                            'Lons':np.array(theRoute.Lon, dtype='float32')} )
            theRoute = myRoutes.iloc[3]
            FlattenedInterstates.append({   'Name':'Interstate 49 (Arkansas-North Segment)',
                                            'Lats':np.array(theRoute.Lat, dtype='float32'),
                                            'Lons':np.array(theRoute.Lon, dtype='float32')} )
            theRoute = myRoutes.iloc[4]
            FlattenedInterstates.append({   'Name':'Interstate 49 (Missouri)',
                                            'Lats':np.array(theRoute.Lat, dtype='float32'),
                                            'Lons':np.array(theRoute.Lon, dtype='float32')} )

        elif (theName == 'Interstate 69'):
            # stitch routes 0 & 1 together
            latlist = np.array([])
            lonlist = np.array([])
            theRoute = myRoutes.iloc[0]
            latlist = np.append(latlist,np.flipud(theRoute.Lat))
            lonlist = np.append(lonlist,np.flipud(theRoute.Lon))
            theRoute = myRoutes.iloc[1]
            latlist = np.append(latlist,(theRoute.Lat))
            lonlist = np.append(lonlist,(theRoute.Lon))
            FlattenedInterstates.append({   'Name':theName,
                                            'Lats':np.array(latlist, dtype='float32'),
                                            'Lons':np.array(lonlist, dtype='float32')} )

        elif (theName == 'Interstate 878 (New York)'):
            # keep first route only
            theRoute = myRoutes.iloc[0]
            FlattenedInterstates.append({   'Name':theName,
                                            'Lats':np.array(theRoute.Lat, dtype='float32'),
                                            'Lons':np.array(theRoute.Lon, dtype='float32')} )

        elif (theName == 'Interstate 265 (Indiana)'):
            # keep SECOND route only
            theRoute = myRoutes.iloc[1]
            FlattenedInterstates.append({   'Name':theName,
                                            'Lats':np.array(theRoute.Lat, dtype='float32'),
                                            'Lons':np.array(theRoute.Lon, dtype='float32')} )

        elif (theName == 'Interstate 587 (New York)'):
            # stitch all routes together (in a super weird order wtf)
            latlist = np.array([])
            lonlist = np.array([])
            theRoute = myRoutes.iloc[0]
            latlist = np.append(latlist,np.flipud(theRoute.Lat))
            lonlist = np.append(lonlist,np.flipud(theRoute.Lon))
            theRoute = myRoutes.iloc[1]
            latlist = np.append(latlist,(theRoute.Lat))
            lonlist = np.append(lonlist,(theRoute.Lon))
            theRoute = myRoutes.iloc[3]
            latlist = np.append(latlist,(theRoute.Lat))
            lonlist = np.append(lonlist,(theRoute.Lon))
            theRoute = myRoutes.iloc[2]
            latlist = np.append(latlist,np.flipud(theRoute.Lat))
            lonlist = np.append(lonlist,np.flipud(theRoute.Lon))
            theRoute = myRoutes.iloc[4]
            latlist = np.append(latlist,(theRoute.Lat))
            lonlist = np.append(lonlist,(theRoute.Lon))
            theRoute = myRoutes.iloc[5]
            latlist = np.append(latlist,(theRoute.Lat))
            lonlist = np.append(lonlist,(theRoute.Lon))
            theRoute = myRoutes.iloc[7]
            latlist = np.append(latlist,(theRoute.Lat))
            lonlist = np.append(lonlist,(theRoute.Lon))
            theRoute = myRoutes.iloc[6]
            latlist = np.append(latlist,np.flipud(theRoute.Lat))
            lonlist = np.append(lonlist,np.flipud(theRoute.Lon))
            theRoute = myRoutes.iloc[8]
            latlist = np.append(latlist,(theRoute.Lat))
            lonlist = np.append(lonlist,(theRoute.Lon))
            theRoute = myRoutes.iloc[9]
            latlist = np.append(latlist,(theRoute.Lat))
            lonlist = np.append(lonlist,(theRoute.Lon))
            theRoute = myRoutes.iloc[10]
            latlist = np.append(latlist,np.flipud(theRoute.Lat))
            lonlist = np.append(lonlist,np.flipud(theRoute.Lon))
            theRoute = myRoutes.iloc[12]
            latlist = np.append(latlist,(theRoute.Lat))
            lonlist = np.append(lonlist,(theRoute.Lon))
            theRoute = myRoutes.iloc[11]
            latlist = np.append(latlist,(theRoute.Lat))
            lonlist = np.append(lonlist,(theRoute.Lon))
            theRoute = myRoutes.iloc[13]
            latlist = np.append(latlist,(theRoute.Lat))
            lonlist = np.append(lonlist,(theRoute.Lon))
            theRoute = myRoutes.iloc[14]
            latlist = np.append(latlist,(theRoute.Lat))
            lonlist = np.append(lonlist,(theRoute.Lon))
            # theRoute = myRoutes.iloc[18]
            # latlist = np.append(latlist,(theRoute.Lat))
            # lonlist = np.append(lonlist,(theRoute.Lon))
            # theRoute = myRoutes.iloc[17]
            # latlist = np.append(latlist,(theRoute.Lat))
            # lonlist = np.append(lonlist,(theRoute.Lon))
            # theRoute = myRoutes.iloc[16]
            # latlist = np.append(latlist,np.flipud(theRoute.Lat))
            # lonlist = np.append(lonlist,np.flipud(theRoute.Lon))
            theRoute = myRoutes.iloc[15]
            latlist = np.append(latlist,(theRoute.Lat))
            lonlist = np.append(lonlist,(theRoute.Lon))
            theRoute = myRoutes.iloc[19]
            latlist = np.append(latlist,(theRoute.Lat))
            lonlist = np.append(lonlist,(theRoute.Lon))
            theRoute = myRoutes.iloc[20]
            latlist = np.append(latlist,(theRoute.Lat))
            lonlist = np.append(lonlist,(theRoute.Lon))
            theRoute = myRoutes.iloc[22]
            latlist = np.append(latlist,(theRoute.Lat))
            lonlist = np.append(lonlist,(theRoute.Lon))
            theRoute = myRoutes.iloc[23]
            latlist = np.append(latlist,(theRoute.Lat))
            lonlist = np.append(lonlist,(theRoute.Lon))
            theRoute = myRoutes.iloc[24]
            latlist = np.append(latlist,(theRoute.Lat))
            lonlist = np.append(lonlist,(theRoute.Lon))
            theRoute = myRoutes.iloc[21]
            latlist = np.append(latlist,(theRoute.Lat))
            lonlist = np.append(lonlist,(theRoute.Lon))
            FlattenedInterstates.append({   'Name':theName,
                                            'Lats':np.array(latlist, dtype='float32'),
                                            'Lons':np.array(lonlist, dtype='float32')} )

        elif (theName == 'Interstate 140 (North Carolina)'):
            # keep first route only
            theRoute = myRoutes.iloc[0]
            FlattenedInterstates.append({   'Name':theName,
                                            'Lats':np.array(theRoute.Lat, dtype='float32'),
                                            'Lons':np.array(theRoute.Lon, dtype='float32')} )

        elif (theName == 'Interstate 790 (New York)'):
            # keep first route only
            theRoute = myRoutes.iloc[0]
            FlattenedInterstates.append({   'Name':theName,
                                            'Lats':np.array(theRoute.Lat, dtype='float32'),
                                            'Lons':np.array(theRoute.Lon, dtype='float32')} )

        elif (theName == 'Interstate 83'):
            # keep first route only
            theRoute = myRoutes.iloc[0]
            FlattenedInterstates.append({   'Name':theName,
                                            'Lats':np.array(theRoute.Lat, dtype='float32'),
                                            'Lons':np.array(theRoute.Lon, dtype='float32')} )

        elif (theName == 'Interstate 840 (North Carolina)'):
            # keep first route only
            theRoute = myRoutes.iloc[0]
            FlattenedInterstates.append({   'Name':theName,
                                            'Lats':np.array(theRoute.Lat, dtype='float32'),
                                            'Lons':np.array(theRoute.Lon, dtype='float32')} )

        elif (theName == 'Interstate 376 (Pennsylvania)'):
            # keep first route only
            theRoute = myRoutes.iloc[0]
            FlattenedInterstates.append({   'Name':theName,
                                            'Lats':np.array(theRoute.Lat, dtype='float32'),
                                            'Lons':np.array(theRoute.Lon, dtype='float32')} )

        else:
            print("***** 2+ Routes but IF/ELSE MISSED IT *****   "+theName)
    elif numRoutes>0:
        # add this individual (by title) to the dataframe
        theRoute = myRoutes.iloc[0]
        FlattenedInterstates.append({   'Name':theName,
                                        'Lats':np.array(theRoute.Lat, dtype='float32'),
                                        'Lons':np.array(theRoute.Lon, dtype='float32')} )
    else:
        print("***** This Interstate has No Routes:     "+interstate['title'])

#
FlattenedInterstates = pd.DataFrame(FlattenedInterstates)



################################################################################
################################################################################
###             Organize interstates by direction and length                 ###
################################################################################
################################################################################

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
# go through and delete all the short ones (under 2 km)
# (record sizes)
FlattenedInterstates['Dist'] = FlattenedInterstates['Lats'] # add dummy data to "Dist" Column
FlattenedInterstates['Length'] = FlattenedInterstates['Lats'] # add dummy data to "Dist" Column
FlattenedInterstates['Direction'] = FlattenedInterstates['Name'] # add dummy data to "Direction" Column
for index, interstate in FlattenedInterstates.iterrows():
    Lats = interstate.Lats
    Lons = interstate.Lons

    EWDistance = greatCircleDistance(Lons[0],Lats[0],Lons[-1],Lats[0])
    NSDistance = greatCircleDistance(Lons[0],Lats[0],Lons[0],Lats[-1])
    if (EWDistance>NSDistance):
        #this is an east west road
        FlattenedInterstates.set_value(index,'Direction','East')
        if (Lons[0]>Lons[-1]):
            # flip it to make it eastbound
            Lats = np.flipud(Lats)
            Lons = np.flipud(Lons)
            FlattenedInterstates.set_value(index,'Lats',Lats)
            FlattenedInterstates.set_value(index,'Lons',Lons)
        plt.plot(Lons,Lats,'g')
    else:
        FlattenedInterstates.set_value(index,'Direction','South')
        #this is a north south road
        if (Lats[0]<Lats[-1]):
            # flip it to make it southbound
            Lats = np.flipud(Lats)
            Lons = np.flipud(Lons)
            FlattenedInterstates.set_value(index,'Lats',Lats)
            FlattenedInterstates.set_value(index,'Lons',Lons)
        plt.plot(Lons,Lats,'b')

    Dist = 0*Lats
    for ii in (range(Lons.size-1)):
        Dist[ii+1] = Dist[ii]+greatCircleDistance(Lons[ii+1],Lats[ii+1], Lons[ii],Lats[ii])
    FlattenedInterstates.set_value(index,'Dist',Dist)
    FlattenedInterstates.set_value(index,'Length',Dist[-1])
plt.show()
print(FlattenedInterstates)


################################################################################
################################################################################
###                     Filter out the short ones                            ###
################################################################################
################################################################################

LongEnoughInterstates = FlattenedInterstates.loc[ FlattenedInterstates['Length'] >8.04672] # 5 miles
for index, interstate in LongEnoughInterstates.iterrows():
    Lats = interstate.Lats
    Lons = interstate.Lons
    plt.plot(Lons,Lats,'k')
plt.show()
print(LongEnoughInterstates)

Interstates = LongEnoughInterstates


pickle.dump(Interstates,open(thisRepo+"data/interim/Interstates.p","wb"))

import pickle
import json
import shapely.geometry as shp
import pandas as pd
import math
from copy import deepcopy

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
    
def dijkstra(graph,src,dest,visited=[],distances={},predecessors={}):
    # a few sanity checks
    if src not in graph:
        raise TypeError('The root of the shortest path tree cannot be found')
    if dest not in graph:
        raise TypeError('The target of the shortest path cannot be found')    
    # ending condition
    if src == dest:
        # We build the shortest path and display it
        path=[]
        pred=dest
        while pred != None:
            path.append(pred)
            pred=predecessors.get(pred,None)
        path.reverse()
        print('shortest path: '+str(path)+" cost="+str(distances[dest]))
        return path
    else :     
        # if it is the initial  run, initializes the cost
        if not visited: 
            distances[src]=0
        # visit the neighbors
        for neighbor in graph[src] :
            if neighbor not in visited:
                new_distance = distances[src] + graph[src][neighbor]
                if new_distance < distances.get(neighbor,float('inf')):
                    distances[neighbor] = new_distance
                    predecessors[neighbor] = src
        # mark as visited
        visited.append(src)
        # now that all neighbors have been visited: recurse                         
        # select the non visited node with lowest distance 'x'
        # run Dijskstra with src='x'
        unvisited={}
        for k in graph:
            if k not in visited:
                unvisited[k] = distances.get(k,float('inf'))        
        x=min(unvisited, key=unvisited.get)
        return dijkstra(graph,x,dest,visited,distances,predecessors)    
    

# First do a very coarse MultiLineString of all the highways
# (for the background art)
#interstateList = []
#for idx, interstate in interstates.iterrows():
#    #if (idx>10):
#    #    break
#    print("##############"+str(idx))
#    pathFrame = interstate['Path']
#    thisLine = []
#    for jdx, coordinate in pathFrame.iterrows():
#        # build the path content        
#        mySegmentLon = round(pathFrame['lon'][jdx],3)
#        mySegmentLat = round(pathFrame['lat'][jdx],3)
#        mySegment = [mySegmentLon, mySegmentLat]
#        thisLine.append(mySegment)
#    #simplify the line if possible for smaller filesize
#    if (len(thisLine)>1):
#        line = shp.LineString(thisLine)
#        simpleLine = line.simplify(0.025)
#        thisLine = simpleLine.coords[:]           
#    interstateList.append(thisLine)
#    
#interstateMLS = {'type':'MultiLineString', 'coordinates':interstateList}
#with open(thisRepo+"report/data/interstatePaths.json", 'wb') as outfile:
#        json.dump(interstateMLS, outfile)



# Now get the path for each Dijkstra Edge from the interstate data
nodes = [ {'x':-117.147523, 'y': 32.713364, 'name': 'San Diego',    'ind': '0'},
          {'x':-118.214194, 'y': 34.055253, 'name': 'Los Angeles',  'ind': '1'},
          {'x':-122.405445, 'y': 37.769633, 'name': 'San Francisco','ind': '2'},
          {'x':-121.517006, 'y': 38.624906, 'name': 'Sacramento',   'ind': '3'},
          {'x':-122.320158, 'y': 47.594245, 'name': 'Seattle',      'ind': '4'},
          {'x':-106.730233, 'y': 32.260806, 'name': 'Las Cruces',   'ind': '5'},
          {'x':-106.628958, 'y': 35.105298, 'name': 'Albuquerque',  'ind': '6'},
          {'x':-104.851108, 'y': 41.113133, 'name': 'Cheyenne',     'ind': '7'},
          {'x':-106.689959, 'y': 44.373141, 'name': 'Buffalo',      'ind': '8'},
          {'x':-90.438027,  'y': 30.087304, 'name': 'New Orleans',  'ind': '9'},
          {'x':-90.149866,  'y': 35.155328, 'name': 'Memphis',      'ind': '10'},
          {'x':-88.196753,  'y': 41.486098, 'name': 'Illinois',     'ind': '11'},
          {'x':-87.641616,  'y': 41.847058, 'name': 'Chicago',      'ind': '12'},
          {'x':-80.209319,  'y': 25.750145, 'name': 'Miami',        'ind': '13'},
          {'x':-81.657962,  'y': 30.314470, 'name': 'Jacksonville', 'ind': '14'},
          {'x':-78.517799,  'y': 35.389918, 'name': 'Raleigh',      'ind': '15'},
          {'x':-74.011409,  'y': 40.864572, 'name': 'New York',     'ind': '16'},
          {'x':-71.262004,  'y': 42.340561, 'name': 'Boston',       'ind': '17'} ]
              
edges = [ {'id':1,   'name':'5',  'd':'S', 'srce':1,  'dest':0},
          {'id':2,   'name':'5',  'd':'S', 'srce':3,  'dest':1},
          {'id':3,   'name':'5',  'd':'S', 'srce':4,  'dest':3},
          {'id':4,   'name':'25', 'd':'S', 'srce':6,  'dest':5},
          {'id':5,   'name':'25', 'd':'S', 'srce':7,  'dest':6},
          {'id':6,   'name':'25', 'd':'S', 'srce':8,  'dest':7},
          {'id':7,   'name':'55', 'd':'S', 'srce':10, 'dest':9},
          {'id':8,   'name':'55', 'd':'S', 'srce':11, 'dest':10},
          {'id':9,   'name':'55', 'd':'S', 'srce':12, 'dest':11},
          {'id':10,  'name':'95', 'd':'S', 'srce':14, 'dest':13},
          {'id':11,  'name':'95', 'd':'S', 'srce':15, 'dest':14},
          {'id':12,  'name':'95', 'd':'S', 'srce':16, 'dest':15},
          {'id':13,  'name':'95', 'd':'S', 'srce':17, 'dest':16},
          {'id':14,  'name':'10', 'd':'E', 'srce':1,  'dest':5},
          {'id':15,  'name':'10', 'd':'E', 'srce':5,  'dest':9},
          {'id':16,  'name':'10', 'd':'E', 'srce':9,  'dest':14},
          {'id':17,  'name':'40', 'd':'E', 'srce':6,  'dest':10},
          {'id':18,  'name':'40', 'd':'E', 'srce':10, 'dest':15},
          {'id':19,  'name':'80', 'd':'E', 'srce':2,  'dest':3},
          {'id':20,  'name':'80', 'd':'E', 'srce':3,  'dest':7},
          {'id':21,  'name':'80', 'd':'E', 'srce':7,  'dest':11},
          {'id':22,  'name':'80', 'd':'E', 'srce':11, 'dest':16},
          {'id':23,  'name':'90', 'd':'E', 'srce':4,  'dest':8},
          {'id':24,  'name':'90', 'd':'E', 'srce':8,  'dest':12},
          {'id':25,  'name':'90', 'd':'E', 'srce':12, 'dest':17},
          {'id':101, 'name':'5',  'd':'N', 'srce':0,  'dest':1},
          {'id':102, 'name':'5',  'd':'N', 'srce':1,  'dest':3},
          {'id':103, 'name':'5',  'd':'N', 'srce':3,  'dest':4},
          {'id':104, 'name':'25', 'd':'N', 'srce':5,  'dest':6},
          {'id':105, 'name':'25', 'd':'N', 'srce':6,  'dest':7},
          {'id':106, 'name':'25', 'd':'N', 'srce':7,  'dest':8},
          {'id':107, 'name':'55', 'd':'N', 'srce':9,  'dest':10},
          {'id':108, 'name':'55', 'd':'N', 'srce':10, 'dest':11},
          {'id':109, 'name':'55', 'd':'N', 'srce':11, 'dest':12},
          {'id':110, 'name':'95', 'd':'N', 'srce':13, 'dest':14},
          {'id':111, 'name':'95', 'd':'N', 'srce':14, 'dest':15},
          {'id':112, 'name':'95', 'd':'N', 'srce':15, 'dest':16},
          {'id':113, 'name':'95', 'd':'N', 'srce':16, 'dest':17},
          {'id':114, 'name':'10', 'd':'W', 'srce':5,  'dest':1},
          {'id':115, 'name':'10', 'd':'W', 'srce':9,  'dest':5},
          {'id':116, 'name':'10', 'd':'W', 'srce':14, 'dest':9},
          {'id':117, 'name':'40', 'd':'W', 'srce':10, 'dest':6},
          {'id':118, 'name':'40', 'd':'W', 'srce':15, 'dest':10},
          {'id':119, 'name':'80', 'd':'W', 'srce':3,  'dest':2},
          {'id':120, 'name':'80', 'd':'W', 'srce':7,  'dest':3},
          {'id':121, 'name':'80', 'd':'W', 'srce':11, 'dest':7},
          {'id':122, 'name':'80', 'd':'W', 'srce':16, 'dest':11},
          {'id':123, 'name':'90', 'd':'W', 'srce':8,  'dest':4},
          {'id':124, 'name':'90', 'd':'W', 'srce':12, 'dest':8},
          {'id':125, 'name':'90', 'd':'W', 'srce':17, 'dest':12} ]              
routeDict = {'5':209, '25':144, '55':0, '95':62, '10':50, '40':169, '80':166, '90':3}
# 95 Northern Segment is 63

newEdges = []
for edge in edges:
    print(edge['name']+' - '+str(edge['id']))
    ind = routeDict[edge['name']]
    id=edge['id']
    if ((id==13)|(id==113)):
        ind = 63
    interstate = interstates.loc[ind]
    reverse = (id>100)
    if reverse:
        lastEnd = edge['srce']
        firstEnd = edge['dest']
        cityCol = 'destAgainst_UniqueNameDests'
    else:
        firstEnd = edge['srce']
        lastEnd = edge['dest']
        cityCol = 'destWith_UniqueNameDests'
    firstEndLat = round(nodes[firstEnd]['y'],3)
    firstEndLon = round(nodes[firstEnd]['x'],3) 
    lastEndLat  = round(nodes[lastEnd]['y'],3)
    lastEndLon  = round(nodes[lastEnd]['x'],3)
    
    pathFrame = interstate['Path']
    for jdx, coordinate in pathFrame.iterrows():
        # build the path content        
        mySegmentLon = round(pathFrame['lon'][jdx],3)
        mySegmentLat = round(pathFrame['lat'][jdx],3)
        mySegmentIndx = jdx
        distToFirst = greatCircleDistance(mySegmentLon,mySegmentLat,firstEndLon,firstEndLat)
        distToLast  = greatCircleDistance(mySegmentLon,mySegmentLat,lastEndLon, lastEndLat)
        if (distToFirst<5):
            startJdx = mySegmentIndx
        if (distToLast<5):
            lastJdx = mySegmentIndx
            break
    # catch the cases where I-95 doesn't quite connect DC to NY
    if (id==12):
        startJdx = 0
    elif (id==112):
        lastJdx = mySegmentIndx
    
    #build up the path
    jsonPath = [] 
    jsonPath.append({'x':firstEndLon, 'y':firstEndLat, 'c':nodes[firstEnd]['name']})
    for jdx, coordinate in pathFrame.iterrows():
        if ((jdx>=startJdx)&(jdx<=lastJdx)):
            mySegmentLon = round(pathFrame['lon'][jdx],3)
            mySegmentLat = round(pathFrame['lat'][jdx],3)
            myC = ''
            myCpop = 0
            # get the biggest City on the list
            if cityCol in pathFrame.columns:
                myDestIDs = pathFrame[cityCol][jdx] 
            else:
                myDestIDs = []
            for destID in myDestIDs:
                if (int(destID)>0):
                    thisName = cities.loc[int(destID)].city_ascii
                    thisPop = cities.loc[int(destID)].population
                    if (thisPop>myCpop):
                        myCpop = thisPop
                        myC = thisName
            jsonPath.append({'x':mySegmentLon,  'y':mySegmentLat,  'c':myC})
    jsonPath.append({'x':lastEndLon, 'y':lastEndLat, 'c':nodes[lastEnd]['name']})
    if reverse:
        jsonPath.reverse()
    
    #compress it down (it's probably way too detailed)
    # if you've been successful at shrinking, keep shrinking
    # take out odd indexes who are <5km from  both neighbors and who's 'c' matches both neighbors
    shrinkage = True
    Ni = len(jsonPath)
    while shrinkage:
        shrinkage = False
        indsToDelete = []
        N = len(jsonPath)
        for ii in range(1,N-1,2):
            myC = jsonPath[ii]['c']
            aC = jsonPath[ii-1]['c']
            bC = jsonPath[ii+1]['c']
            dist1 = greatCircleDistance(jsonPath[ii]['x'],jsonPath[ii]['y'],jsonPath[ii-1]['x'],jsonPath[ii-1]['y'])
            dist2 = greatCircleDistance(jsonPath[ii]['x'],jsonPath[ii]['y'],jsonPath[ii+1]['x'],jsonPath[ii+1]['y'])
            if ((myC==aC)&(myC==bC)&(dist1<50)&(dist2<50)):
                indsToDelete.append(ii)
                shrinkage = True
        jsonPath = [i for j, i in enumerate(jsonPath) if j not in indsToDelete]
    Nf = len(jsonPath)
    print('shrunk path from: '+str(Ni)+' to '+str(Nf)+' segments')
    
    # go use great circle dists to do the lengths
    N = len(jsonPath)
    jsonPath[0]['L'] = 0
    cumL = 0
    for ii in range(1,N):
        L = greatCircleDistance(jsonPath[ii]['x'],jsonPath[ii]['y'],jsonPath[ii-1]['x'],jsonPath[ii-1]['y'])
        jsonPath[ii]['L'] = round(L,3)
        cumL += L
    
    # finish it up to save it
    newEdge = {'id':id, 'name':edge['name'], 'd':edge['d'], 'dest':edge['dest'], 'length': round(cumL,3), 'route':jsonPath}
    newEdges.append(newEdge)
with open(thisRepo+"report/data/dijkstraEdges.json", 'wb') as outfile:
    json.dump(newEdges, outfile)  
    
    
#with open(thisRepo+"report/data/dijkstraEdges.json") as json_data:
#     newEdges = json.load(json_data)
    
    
# Now actually solve the shortest path for all combinations using Dijkstras Alg  
connectivity = {'0': {'1': newEdges[1-1]['length']},
                '1': {'0': newEdges[1-1]['length'],   '3': newEdges[2-1]['length'],   '5': newEdges[14-1]['length']},
                '2': {'3': newEdges[19-1]['length']},
                '3': {'1': newEdges[2-1]['length'],   '2': newEdges[19-1]['length'],  '4': newEdges[3-1]['length'],  '7': newEdges[20-1]['length']},
                '4': {'3': newEdges[3-1]['length'],   '8': newEdges[23-1]['length']},
                '5': {'1': newEdges[14-1]['length'],  '6': newEdges[4-1]['length'],   '9': newEdges[15-1]['length']},
                '6': {'5': newEdges[4-1]['length'],   '7': newEdges[5-1]['length'],   '10':newEdges[17-1]['length']},
                '7': {'6': newEdges[5-1]['length'],   '3': newEdges[20-1]['length'],  '8': newEdges[6-1]['length'],  '11':newEdges[21-1]['length']},
                '8': {'7': newEdges[6-1]['length'],   '4': newEdges[23-1]['length'],  '12':newEdges[24-1]['length']},
                '9': {'5': newEdges[15-1]['length'],  '10':newEdges[7-1]['length'],   '14':newEdges[16-1]['length']},
                '10':{'9': newEdges[7-1]['length'],   '6': newEdges[17-1]['length'],  '11':newEdges[8-1]['length'],  '15': newEdges[18-1]['length']},
                '11':{'10':newEdges[8-1]['length'],   '7': newEdges[21-1]['length'],  '12':newEdges[9-1]['length'],  '16': newEdges[22-1]['length']},
                '12':{'11':newEdges[9-1]['length'],   '8': newEdges[24-1]['length'],  '17':newEdges[25-1]['length']},
                '13':{'14':newEdges[10-1]['length']},
                '14':{'13':newEdges[10-1]['length'],  '9': newEdges[16-1]['length'],  '15':newEdges[11-1]['length']},
                '15':{'14':newEdges[11-1]['length'],  '10':newEdges[18-1]['length'],  '16':newEdges[12-1]['length']},
                '16':{'15':newEdges[12-1]['length'],  '11':newEdges[22-1]['length'],  '17':newEdges[13-1]['length']},
                '17':{'16':newEdges[13-1]['length'],  '12':newEdges[25-1]['length']}
                }
numNodes = len(nodes)
routesDJ = []
for ii_from in range(numNodes):
    routesVec = []
    for ii_to in range(numNodes):
        if (ii_from==ii_to):
            # trivial case
            thisRoute = []
        else:
            # do Dijkstra
            myGraph = deepcopy(connectivity)
            dj = dijkstra(myGraph, str(ii_from), str(ii_to),[],{},{})
            thisRoute = []
            LL = len(dj)
            for jj in range(1,LL):
                startAt = dj[jj-1]
                endAt   = dj[jj]
                theEdge = filter(lambda x: x['dest']==int(endAt), filter(lambda x: x['srce']==int(startAt), edges))
                thisRoute.append(theEdge[0]['id'])

        routesVec.append(thisRoute)
    routesDJ.append(routesVec)
with open(thisRepo+"report/data/dijkstraRoutes.json", 'wb') as outfile:
    json.dump(routesDJ, outfile)   
    
    
    
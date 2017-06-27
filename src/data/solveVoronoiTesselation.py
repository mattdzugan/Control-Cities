import pickle
import numpy as np
from scipy.spatial import Voronoi, voronoi_plot_2d
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
import shapely.geometry as shp
import math

thisRepo = '/home/mattdzugan/Documents/dev/Control Cities/'

# UID, InterstateName, Number, PickleIndex, thisOrigin, thisDestin, theseWayps, startsForward, tfparam1, tfparam2
interstates = pickle.load(open(thisRepo+"data/interim/InterstatesWithConsolidated.p","rb"))

CONUS_lonlat = np.loadtxt(open(thisRepo+"/data/Raw/CONUS.geo.csv", "rb"), delimiter=",", skiprows=1)
CONUS_poly = shp.Polygon(CONUS_lonlat)
CONUS_box = np.array([  [-180.0,90.0],
                        [180.0, 90.0],
                        [180.0, -90.0],
                        [-180.0,-90.0] ])
#CONUS_lonlat

interstateLonLats = np.empty([0,2])
interstatePointIDs = []
for idx, interstate in interstates.iterrows():
    thisLats = np.array(interstate.Lats)
    thisLons = np.array(interstate.Lons)
    thisLonLat = np.transpose(np.vstack((thisLons,thisLats)))

    pathFrame = interstate['Path']
    thisIDs = np.array(pathFrame.pointID)
    #thisIDs = np.transpose(thisIDs)
    #print(thisLonLat.shape)
    interstateLonLats = np.vstack((interstateLonLats,thisLonLat))
    interstatePointIDs = np.hstack((interstatePointIDs,thisIDs))

################################################################################
################################################################################
###                         Useful Functions                                 ###
################################################################################
################################################################################
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
pickle.dump(VoronoiResults, open(thisRepo + "data/interim/InterstateVoronoi.p", "wb"))


p = PatchCollection(patches, cmap=matplotlib.cm.jet, alpha=0.4)
colors = 100*np.random.rand(len(patches))
p.set_array(np.array(colors))
ax.add_collection(p)
ax.set_xlim(-130, -60)
ax.set_ylim(20, 60)
plt.show()

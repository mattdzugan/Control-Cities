import pickle
import math as math
import numpy as np
import pandas as pd

thisRepo = '/home/mattdzugan/Documents/dev/Control Cities/'

################################################################################
###                         Create Task List                                 ###
################################################################################
interstates = pickle.load(open(thisRepo+"data/interim/Interstates.p","rb"))
TaskList = []
UID = 0
for idx, interstate in interstates.iterrows():

    InterstateName =interstate.Name
    InterstateNumber = int(filter(str.isdigit, interstate.Name))
    PickleIndex = idx

    # For each Iterstate create 3 recipes of instrucitons-sets
    N = interstate.Lats.shape[0]
    N1 = 0
    N2 = math.ceil(N/2)
    count = 0

    nn1 = N1
    nn2 = N2

    recipe1 = [] #recipe 1 is the efficient one
    recipe2 = [] #recipe 2 iterates from middle-start-middle-1-start-middle-2-start
    recipe3 = [] #recipe 3 iterates from middle-end-middle+1-end-middle+2-end
    idlist = []
    while nn2<N:
        idlist.append(nn1)
        nn1+=1
        count+=1
        idlist.append(nn2)
        nn2+=1
        count+=1
        if (count>21): #21 (8 for I-90 index3)
            idlist.append(nn1)
            #print(idlist)
            recipe1.append(np.array(idlist))
            idlist = []
            count = 0
    idlist = []
    nn = N2
    count =0
    while nn>0:
        idlist.append(nn)
        idlist.append(0)
        nn-=1
        count+=2
        if (count>22): #22 (8 for I-90 index3)
            recipe2.append(np.array(idlist))
            idlist = []
            count = 0

    idlist = []
    nn = N2
    count =0
    while nn<(N-1):
        idlist.append(nn)
        idlist.append(N-1)
        nn+=1
        count+=2
        if (count>22): #22 (6 for I-90 index3)
            recipe3.append(np.array(idlist))
            idlist = []
            count = 0


    ############################################################################
    ###                       Write To TaskList                              ###
    ############################################################################

    ###                             Recipe1                                      ###
    for thisIDList in recipe1:
        thisOrigin = (interstate.Lats[thisIDList[0]],   interstate.Lons[thisIDList[0]])
        thisDestin = (interstate.Lats[thisIDList[-1]],  interstate.Lons[thisIDList[-1]])
        theseWayps = []
        for idVal in thisIDList[1:-1]:
            theseWayps.append( (interstate.Lats[idVal]+0.02,interstate.Lons[idVal]+0.02) )
        TaskList.append({   'UID':UID,
                            'InterstateName':InterstateName,
                            'Number':InterstateNumber,
                            'PickleIndex':PickleIndex,
                            'thisOrigin':thisOrigin,
                            'thisDestin':thisDestin,
                            'theseWayps':theseWayps,
                            'startsForward':True,
                            'tfparam1':True,
                            'tfparam2':True } )
        UID+=1


    ###                             Recipe2                                      ###
    for thisIDList in recipe2:
        thisOrigin = (interstate.Lats[thisIDList[0]],   interstate.Lons[thisIDList[0]])
        thisDestin = (interstate.Lats[thisIDList[-1]],  interstate.Lons[thisIDList[-1]])
        theseWayps = []
        for idVal in thisIDList[1:-1]:
            theseWayps.append( (interstate.Lats[idVal]+0.02,interstate.Lons[idVal]+0.02) )
        TaskList.append({   'UID':UID,
                            'InterstateName':InterstateName,
                            'Number':InterstateNumber,
                            'PickleIndex':PickleIndex,
                            'thisOrigin':thisOrigin,
                            'thisDestin':thisDestin,
                            'theseWayps':theseWayps,
                            'startsForward':False,
                            'tfparam1':True,
                            'tfparam2':False } )
        UID+=1


    ###                             Recipe3                                      ###
    for thisIDList in recipe3:
        thisOrigin = (interstate.Lats[thisIDList[0]],   interstate.Lons[thisIDList[0]])
        thisDestin = (interstate.Lats[thisIDList[-1]],  interstate.Lons[thisIDList[-1]])
        theseWayps = []
        for idVal in thisIDList[1:-1]:
            theseWayps.append( (interstate.Lats[idVal]+0.02,interstate.Lons[idVal]+0.02) )
        TaskList.append({   'UID':UID,
                            'InterstateName':InterstateName,
                            'Number':InterstateNumber,
                            'PickleIndex':PickleIndex,
                            'thisOrigin':thisOrigin,
                            'thisDestin':thisDestin,
                            'theseWayps':theseWayps,
                            'startsForward':True,
                            'tfparam1':True,
                            'tfparam2':False } )
        UID+=1


################################################################################
###                          Save Task List                                  ###
################################################################################

TaskList = pd.DataFrame(TaskList)
pickle.dump(TaskList,open(thisRepo+"data/interim/TaskList.p","wb"))
writer = pd.ExcelWriter(thisRepo+"data/interim/TaskList.xlsx")
TaskList.to_excel(writer,'Sheet1')

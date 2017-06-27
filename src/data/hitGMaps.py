import pickle
import math as math
import numpy as np
import pandas as pd
import googlemaps
import time
import os.path
import re

thisRepo = '/home/mattdzugan/Documents/dev/Control Cities/'
with open(thisRepo+'src/config/googlekey.txt', 'r') as myfile:
    gkey=myfile.read().strip()
gmaps = googlemaps.Client(key=gkey)

# UID, InterstateName, Number, PickleIndex, thisOrigin, thisDestin, theseWayps, startsForward, tfparam1, tfparam2
TaskList = pickle.load(open(thisRepo+"data/interim/TaskList.p","rb"))

mostRecentHit = time.time()
timeInverval = 0.02   #35 seconds = free,   #0.02 = paid



################################################################################
################################################################################
###                         Useful Functions                                 ###
################################################################################
################################################################################


def findControlCitiesForThisRoute(thisInterstateNumber,thisDirectionResult,startsForward,useEvenLegs,useOddLegs):
    interstateNumber =  thisInterstateNumber
    outdata = []
    for index, thisleg in enumerate(thisDirectionResult[0]["legs"]):
        if ((((index%2)==0)&(useEvenLegs))|(((index%2)==1)&(useOddLegs))):
            StepByStepDirections = thisleg["steps"]
            for step in StepByStepDirections:
                thisStepStartLat = step["start_location"]["lat"]
                thisStepStartLon = step["start_location"]["lng"]
                thisStepInstucts = step["html_instructions"]
                match = re.search('<b>.*\D*'+str(interstateNumber)+'\D.*\/b>', thisStepInstucts)
                if match:
                    desintations = []
                    if re.search('.*follow signs for.*', thisStepInstucts):
                        pieces = thisStepInstucts.split('follow signs for')
                        for piece in pieces[1:]:
                            controlPoints = piece.split('<b>')
                            for controlPoint in controlPoints[1:]:
                                tag = controlPoint.split('</b>')
                                inner = tag[0]
                                if re.search('^[^0-9]+$', inner):
                                    #got a piece with no numbers
                                    desintations.append(inner)
                    if re.search('.*\(signs for.*', thisStepInstucts):
                        pieces = thisStepInstucts.split('(signs for')
                        for piece in pieces[1:]:
                            controlPoints = piece.split('<b>')
                            for controlPoint in controlPoints[1:]:
                                tag = controlPoint.split('</b>')
                                inner = tag[0]
                                if re.search('^[^0-9]+$', inner):
                                    #got a piece with no numbers
                                    desintations.append(inner)
                    if re.search('.*toward.*', thisStepInstucts):
                        pieces = thisStepInstucts.split('toward')
                        for piece in pieces[1:]:
                            controlPoints = piece.split('<b>')
                            for controlPoint in controlPoints[1:]:
                                tag = controlPoint.split('</b>')
                                inner = tag[0]
                                if re.search('^[^0-9]+$', inner):
                                    #got a piece with no numbers
                                    desintations.append(inner)
                    if re.search('.*ramp to.*', thisStepInstucts):
                        pieces = thisStepInstucts.split('ramp to')
                        for piece in pieces[1:]:
                            controlPoints = piece.split('<b>')
                            for controlPoint in controlPoints[1:]:
                                tag = controlPoint.split('</b>')
                                inner = tag[0]
                                if re.search('^[^0-9]+$', inner):
                                    #got a piece with no numbers
                                    desintations.append(inner)

                    if (len(desintations)>0):
                        #TODO write if this step is going forward or backward
                        if (startsForward&((index%2)==0)):
                            mydir = 1
                        elif ((not(startsForward))&((index%2)==1)):
                            mydir = 1
                        else:
                            mydir = -1
                        destinationString = "     ".join(desintations)
                        outdata.append({
                            "dir":mydir,
                            "lat":thisStepStartLat,
                            "lon":thisStepStartLon,
                            "str":destinationString})
    outdata = pd.DataFrame(outdata)
    return outdata



################################################################################
################################################################################
###                      Initial Pass through Tasks                          ###
################################################################################
################################################################################

for ii in range(5):
    for idx, task in TaskList.iterrows():
        thisInterstateName = task.InterstateName
        thisNumber = task.Number
        thisUID = task.UID
        taskFileDir = thisRepo+'data/interim/directions/I-'+str(thisNumber)+'__'+str(thisInterstateName)+'/'
        taskFileName = 'UID_'+str(thisUID)+'.tsv'
        taskFilePath = taskFileDir+taskFileName
        if not os.path.exists(taskFileDir):
            os.makedirs(taskFileDir)
        if (not(os.path.isfile(taskFilePath))):
            timeSinceLastHit = time.time() - mostRecentHit
            timeToWait = max(0,timeInverval-timeSinceLastHit)
            time.sleep(timeToWait)
            mostRecentHit = time.time()
            try:
                dirs = gmaps.directions(origin=task.thisOrigin, destination=task.thisDestin, waypoints=task.theseWayps)
                outdata = findControlCitiesForThisRoute(thisNumber, dirs, task.startsForward, task.tfparam1, task.tfparam2)
                outdata.to_csv(taskFilePath, sep="\t", encoding='utf-8')
            except:
                print ("Error on initial pass in UID: "+str(thisUID)+" for "+thisInterstateName)


print ("################################################################################")
print ("################################################################################")
print ("###                                                                          ###")
print ("################################################################################")
print ("################################################################################")
################################################################################
################################################################################
###                      Second Pass through Tasks                           ###
################################################################################
################################################################################

for ii in range(3):
    for idx, task in TaskList.iterrows():
        thisInterstateName = task.InterstateName
        thisNumber = task.Number
        thisUID = task.UID
        taskFileDir = thisRepo+'data/interim/directions/I-'+str(thisNumber)+'__'+str(thisInterstateName)+'/'
        taskFileName = 'UID_'+str(thisUID)+'.tsv'
        taskFilePath = taskFileDir+taskFileName
        if not os.path.exists(taskFileDir):
            os.makedirs(taskFileDir)
        if (not(os.path.isfile(taskFilePath))):
            try:
                orig_A = task.thisOrigin
                wayp_A = task.theseWayps[0:2]
                dest_A = task.theseWayps[2]

                orig_B = task.theseWayps[3]
                wayp_B = task.theseWayps[4:6]
                dest_B = task.theseWayps[6]

                orig_C = task.theseWayps[7]
                wayp_C = task.theseWayps[8:10]
                dest_C = task.theseWayps[10]

                orig_D = task.theseWayps[11]
                wayp_D = task.theseWayps[12:14]
                dest_D = task.theseWayps[14]

                orig_E = task.theseWayps[15]
                wayp_E = task.theseWayps[16:18]
                dest_E = task.theseWayps[18]

                orig_F = task.theseWayps[19]
                wayp_F = task.theseWayps[20:]
                dest_F = task.thisDestin

                timeSinceLastHit = time.time() - mostRecentHit
                timeToWait = max(0,timeInverval-timeSinceLastHit)
                time.sleep(timeToWait)
                mostRecentHit = time.time()
                dirs_A = gmaps.directions(origin=orig_A, destination=dest_A, waypoints=wayp_A)
                timeSinceLastHit = time.time() - mostRecentHit
                timeToWait = max(0,timeInverval-timeSinceLastHit)
                time.sleep(timeToWait)
                mostRecentHit = time.time()
                dirs_B = gmaps.directions(origin=orig_B, destination=dest_B, waypoints=wayp_B)
                timeSinceLastHit = time.time() - mostRecentHit
                timeToWait = max(0,timeInverval-timeSinceLastHit)
                time.sleep(timeToWait)
                mostRecentHit = time.time()
                dirs_C = gmaps.directions(origin=orig_C, destination=dest_C, waypoints=wayp_C)
                timeSinceLastHit = time.time() - mostRecentHit
                timeToWait = max(0,timeInverval-timeSinceLastHit)
                time.sleep(timeToWait)
                mostRecentHit = time.time()
                dirs_D = gmaps.directions(origin=orig_D, destination=dest_D, waypoints=wayp_D)
                timeSinceLastHit = time.time() - mostRecentHit
                timeToWait = max(0,timeInverval-timeSinceLastHit)
                time.sleep(timeToWait)
                mostRecentHit = time.time()
                dirs_E = gmaps.directions(origin=orig_E, destination=dest_E, waypoints=wayp_E)
                timeSinceLastHit = time.time() - mostRecentHit
                timeToWait = max(0,timeInverval-timeSinceLastHit)
                time.sleep(timeToWait)
                mostRecentHit = time.time()
                dirs_F = gmaps.directions(origin=orig_F, destination=dest_F, waypoints=wayp_F)

                outdata_A = findControlCitiesForThisRoute(thisNumber, dirs_A, task.startsForward, task.tfparam1, task.tfparam2)
                outdata_B = findControlCitiesForThisRoute(thisNumber, dirs_B, task.startsForward, task.tfparam1, task.tfparam2)
                outdata_C = findControlCitiesForThisRoute(thisNumber, dirs_C, task.startsForward, task.tfparam1, task.tfparam2)
                outdata_D = findControlCitiesForThisRoute(thisNumber, dirs_D, task.startsForward, task.tfparam1, task.tfparam2)
                outdata_E = findControlCitiesForThisRoute(thisNumber, dirs_E, task.startsForward, task.tfparam1, task.tfparam2)
                outdata_F = findControlCitiesForThisRoute(thisNumber, dirs_F, task.startsForward, task.tfparam1, task.tfparam2)

                outdata = outdata_A.append(outdata_B)
                outdata = outdata.append(outdata_C)
                outdata = outdata.append(outdata_D)
                outdata = outdata.append(outdata_E)
                outdata = outdata.append(outdata_F)
                outdata.to_csv(taskFilePath, sep="\t", encoding='utf-8')
            except:
                print("Error on second pass in UID: "+str(thisUID)+" for "+thisInterstateName)





###################################### now catch the "too long" ones
# for ii=1:3 (just to cover my ass in case of network errors)
#   for rr = 1:numRecipes
#      if ./DirectionsData/Success/RecipeID_UID.txt DOES NOT exist
#         thisInterstate is the right one by PickleIndex
#         split route into 6 chunks (A,B,C,D,E,F)
#         * * PAUSE * *
#         findControlCitiesForThisRoute A
#         determine if successful
#            save in ./DirectionsData/Success/RecipeID_UID_A.txt
#         * * PAUSE * *
#         findControlCitiesForThisRoute B
#         determine if successful
#            save in ./DirectionsData/Success/RecipeID_UID_B.txt
#                                           .   .   .   .   .
#         * * PAUSE * *
#         findControlCitiesForThisRoute F
#         determine if successful
#            save in ./DirectionsData/Success/RecipeID_UID_F.txt
#         if all A-F were successful
#            combine and write ./DirectionsData/Success/RecipeID_UID.txt
#         Delete as many of the A-F things that exis

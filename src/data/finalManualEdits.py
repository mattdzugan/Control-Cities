import pickle


thisRepo = '/home/mattdzugan/Documents/dev/Control Cities/'

interstates = pickle.load(open(thisRepo+"data/interim/InterstatesWithCityIDs.p","rb"))
#cities = pd.DataFrame.from_csv(thisRepo+"data/Raw/uscitiesv1.2.csv", index_col=13)


## New Chicago --> Chicago (I90 and I80)
for intind in [3, 166]:
    I = interstates.loc[intind]
    pathFrame = I['Path']
    for direction in ['destWith', 'destAgainst']:
        for jdx, coordinate in pathFrame.iterrows():
            theseDests = coordinate[direction+"_UniqueNameDests"]
            if ('1840009263' in theseDests):
                ind = theseDests.index('1840009263')
                theseDests[ind] = '1840000494'
    
## Two Buffalos on I90
I = interstates.loc[3]
pathFrame = I['Path']
for direction in ['destWith', 'destAgainst']:
    for jdx, coordinate in pathFrame.iterrows():
        theseDests = coordinate[direction+"_UniqueNameDests"]
        mySegmentLon = coordinate['lon']
        if (mySegmentLon<-90.0):
            #WesternUS
            if ('1840000386' in theseDests):
                ind = theseDests.index('1840000386') #replace NY
                theseDests[ind] = '1840018615' #with WY
        else:
            #EasternUS
            if ('1840018615' in theseDests):
                ind = theseDests.index('1840018615') #replace NY
                theseDests[ind] = '1840000386' #with WY


        
## Highway Agnostic ones
for idx, interstate in interstates.iterrows():
    print(idx)
    pathFrame = interstate['Path']
    for direction in ['destWith', 'destAgainst']:
        if (direction+'_UniqueNameDests') in pathFrame.columns:
            for jdx, coordinate in pathFrame.iterrows():
                    theseDests = coordinate[direction+"_UniqueNameDests"]
                    myLon = coordinate['lon']
                    myLat = coordinate['lat']
                    
                    # Radisson Wisconsin --> Madison
                    if ('1840002000' in theseDests):
                        ind = theseDests.index('1840002000') 
                        theseDests[ind] = '1840002915'
                    # Indianola --> 0
                    if ('1840012178' in theseDests):
                        ind = theseDests.index('1840012178') 
                        theseDests[ind] = '0'
                    # Vernon IL --> Mount Vernon
                    if ('1840012849' in theseDests):
                        ind = theseDests.index('1840012849') 
                        theseDests[ind] = '1840008654'
                    # Monroe GA on I20 west of -88 is supposed to be Monroe LA
                    if (('1840014786' in theseDests)&(myLon<-88)):
                        ind = theseDests.index('1840014786') 
                        theseDests[ind] = '1840014881'
                    # Lynn Haven FL --> 0
                    if ('1840015922' in theseDests):
                        ind = theseDests.index('1840015922') 
                        theseDests[ind] = '0'
                    # Michigan ND --> 0
                    if ('1840033057' in theseDests):
                        ind = theseDests.index('1840033057') 
                        theseDests[ind] = '0'
                    # New Hampshire OH --> 0
                    if ('1840026427' in theseDests):
                        ind = theseDests.index('1840026427') 
                        theseDests[ind] = '0'
                    # Mercedes TX --> 0 
                    if ('1840021025' in theseDests):
                        ind = theseDests.index('1840021025') 
                        theseDests[ind] = '0'
                    # Miami north of 35 is --->0
                    if (('1840015149' in theseDests)&(myLat>35)):
                        ind = theseDests.index('1840015149') 
                        theseDests[ind] = '0'
                    # Macon on 75 north of 40 is --->0
                    if (('1840038185' in theseDests)&(myLat>40)):
                        ind = theseDests.index('1840038185') 
                        theseDests[ind] = '0'
                    # Sidney on 80 east of -80 --->0
                    if (('1840009309' in theseDests)&(myLon>-80)):
                        ind = theseDests.index('1840009309') 
                        theseDests[ind] = '0'
                    # Harbor Oregon on 196 ---> 0
                    if ('1840017458' in theseDests):
                        ind = theseDests.index('1840017458') 
                        theseDests[ind] = '0'
                    # Fort Bragg CA on 95s ---> 0
                    if ('1840020189' in theseDests):
                        ind = theseDests.index('1840020189') 
                        theseDests[ind] = '0'
                    # North Baltimore on *** ---> 0
                    if ('1840011560' in theseDests):
                        ind = theseDests.index('1840011560') 
                        theseDests[ind] = '0'
                    # Winchester KY on 81 and 64 East of -80 should be Winchester VA
                    if (('1840015216' in theseDests)&(myLon>-80)):
                        ind = theseDests.index('1840015216') 
                        theseDests[ind] = '1840001623'
                    # Lexington VA on 64 west of -82 should be Lexington KY
                    if (('1840001689' in theseDests)&(myLon<-82)):
                        ind = theseDests.index('1840001689') 
                        theseDests[ind] = '1840015211'
                    # Maine NY on 95N should be ---> 0
                    if ('1840033738' in theseDests):
                        ind = theseDests.index('1840033738') 
                        theseDests[ind] = '0'
                    # Nashville IL on 57 24 should be ---> Nashville TN
                    if ('1840008651' in theseDests):
                        ind = theseDests.index('1840008651') 
                        theseDests[ind] = '1840038081'
                    # Rushville IN on 65 should be ---> Nashville TN
                    if ('1840009553' in theseDests):
                        ind = theseDests.index('1840009553') 
                        theseDests[ind] = '1840038081'
                    # West Chicago on 57 should be ---> Chicago
                    if ('1840010165' in theseDests):
                        ind = theseDests.index('1840010165') 
                        theseDests[ind] = '1840000494'
                    # Ashland OH on 64 should be ---> Ashland KY
                    if ('1840002751' in theseDests):
                        ind = theseDests.index('1840002751') 
                        theseDests[ind] = '1840013195'
                    # Little Flock AR on 540 and 49 should be --> Little Rock
                    if ('1840015284' in theseDests):
                        ind = theseDests.index('1840015284') 
                        theseDests[ind] = '1840015509'
                    # Marlette Mi on 77 --> 0
                    if ('1840002701' in theseDests):
                        ind = theseDests.index('1840002701') 
                        theseDests[ind] = '0'
                    # New Knoxville on 64 ---> Knoxville
                    if ('1840012072' in theseDests):
                        ind = theseDests.index('1840012072') 
                        theseDests[ind] = '1840014486'
                    # New Portland on 95N and 295 ----> Portland ME
                    if ('1840028920' in theseDests):
                        ind = theseDests.index('1840028920') 
                        theseDests[ind] = '1840000327'
                    # Washington Grove MA --> Washington DC
                    if ('1840005860' in theseDests):
                        ind = theseDests.index('1840005860') 
                        theseDests[ind] = '1840006060'
                    # Washington VA --> Washington DC
                    if ('1840006130' in theseDests):
                        ind = theseDests.index('1840006130') 
                        theseDests[ind] = '1840006060'



## Highway Specific ones
# Springfield MO on 72 should be Springfiled IL
I = interstates.loc[298]
pathFrame = I['Path']
for direction in ['destWith', 'destAgainst']:
    for jdx, coordinate in pathFrame.iterrows():
        theseDests = coordinate[direction+"_UniqueNameDests"]
        if ('1840009904' in theseDests):
            ind = theseDests.index('1840009904')
            theseDests[ind] = '1840009517'

pickle.dump(interstates,open(thisRepo+"data/interim/InterstatesWithCityIDs.p","wb"))
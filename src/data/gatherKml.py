import urllib2
from bs4 import BeautifulSoup
from unidecode import unidecode
import re

thisRepo = '/home/mattdzugan/Documents/dev/Control Cities/'

## Go through all of the itnerstates
page = urllib2.urlopen('https://en.wikipedia.org/wiki/List_of_Interstate_Highways').read()
soup = BeautifulSoup(page, 'html.parser')
tableOfInterstates = soup.body.find_all("table")[1]
listOfMainInterstateRows = list(tableOfInterstates.find_all("tr"))[1:]
## Go through all of the auxiliary itnerstates
page = urllib2.urlopen('https://en.wikipedia.org/wiki/List_of_auxiliary_Interstate_Highways').read()
soup = BeautifulSoup(page, 'html.parser')
tableOfInterstates = soup.body.find_all("table")[1]
listOfAuxInterstateRows = list(tableOfInterstates.find_all("tr"))[1:-1]
listOfInterstateRows = listOfMainInterstateRows+listOfAuxInterstateRows
#listOfInterstateRows = listOfInterstateRows[1:]


#for row in listOfInterstateRows[136:139]:
for row in listOfInterstateRows:
    #print(row.th.a)
    myTitle = row.th.a['title'].encode('utf')
    myLink  = row.th.a['href'].encode('utf')
    mySlug = myLink[6:]
    numTds = len(list(row.find_all("td")))
    myStatus = row.find_all("td")[numTds-2].string.encode('utf')
    if (myStatus=="current"):
        try:
            myPage = urllib2.urlopen('https://en.wikipedia.org/w/index.php?title=Template:Attached_KML/' + mySlug + '&action=raw').read()
            mySoup = BeautifulSoup(myPage, 'html.parser')
            # if mySoupe.encode('utf') says #redirect, then redirect
            if ("#REDIRECT" in myPage):
                print(" ")
                print("***REDIRECT*** on write: "+myTitle+"")
                mySlugTemp = re.findall(r'\[\[(.*?)\]\]',myPage,re.DOTALL)
                mySlug = mySlugTemp[0]
                mystr = urllib2.quote('https://en.wikipedia.org/w/index.php?title=' + mySlug + '&action=raw',  safe="%/:=&?~#+!$,;'@()*[]");
                #mystr = 'https://en.wikipedia.org/w/index.php?title=Template:Attached%20KML/Interstate%20540%20and%20North%20Carolina%20Highway%20540&action=raw'
                myPage = urllib2.urlopen(mystr).read()
                mySoup = BeautifulSoup(myPage, 'html.parser')
                f = open(thisRepo+"data/Raw/Wikipedia/"+unidecode(myTitle.decode('utf'))+".kml", "w")
                f.write(mySoup.encode('utf'))
                print("successfully wrote: "+myTitle)
                print(" ")

            else:
                f = open(thisRepo+"data/Raw/Wikipedia/"+unidecode(myTitle.decode('utf'))+".kml", "w")
                f.write(mySoup.encode('utf'))
                print("successfully wrote: "+myTitle)
        except:
            try:
                myPage = urllib2.urlopen('https://en.wikipedia.org/wiki/' + mySlug).read()
                mySoup = BeautifulSoup(myPage, 'html.parser')
                myKmlDiv = mySoup.find_all('table','metadata mbox-small')[-1]
                myLink = myKmlDiv.tr.find_all("td")[1].b.a['href']
                myPage = urllib2.urlopen(myLink).read()
                mySoup = BeautifulSoup(myPage, 'html.parser')
                # if mySoupe.encode('utf') says #redirect, then redirect
                if ("#REDIRECT" in myPage):
                    print(" ")
                    print("***REDIRECT*** on write: "+myTitle+"")
                    mySlugTemp = re.findall(r'\[\[(.*?)\]\]',myPage,re.DOTALL)
                    mySlug = mySlugTemp[0]
                    mystr = urllib2.quote('https://en.wikipedia.org/w/index.php?title=' + mySlug,  safe="%/:=&?~#+!$,;'@()*[]");
                    myPage = urllib2.urlopen(mystr).read()
                    mySoup = BeautifulSoup(myPage, 'html.parser')
                    f = open(thisRepo+"data/Raw/Wikipedia/"+unidecode(myTitle.decode('utf'))+".kml", "w")
                    f.write(mySoup.encode('utf'))
                    print("successfully wrote: "+myTitle)
                    print(" ")
                else:
                    f = open(thisRepo+"data/Raw/Wikipedia/"+unidecode(myTitle.decode('utf'))+".kml", "w")
                    f.write(mySoup.encode('utf'))
                    print("successfully wrote: "+myTitle)
            except:
                print(" ")
                print("***FAILED*** to write: "+myTitle+" due to no kml at either link")
                print(" ")
    else:
        print("DECIDED NOT to write: "+myTitle+"   due to STATUS: "+myStatus)

from bs4 import BeautifulSoup
import requests
import time

# takes in full score (ie 14-23) and returns '14' and '23'
def fixScore(scoreString):
    #awayScore is left of hyphen
    #homeScore is right of hyphen
    hyphen = scoreString.index('-')
    awayScore = scoreString[:hyphen]
    homeScore = scoreString[hyphen+1:]
    return(awayScore,homeScore)

# convert quarter times to time elapsed in game
def fixTime(currentTime,period):

    #fix for OT times being only 5 min
    #2OT: 400489897
    if period < 5:
        elapsed = period - 1
        # add 720 seconds for each quarter 
        addTime = elapsed*720
        semi = currentTime.index(':')
        minutes = int(currentTime[:semi])
        seconds = int(currentTime[semi+1:])

        trueElapsed = 720 - (minutes*60 + seconds) + addTime
        trueMin = trueElapsed//60
        trueSec = trueElapsed%60
        trueTime = str(trueMin) + ":" + str(trueSec)
    else:
        completeOT = period - 5
        addTime = 2880 + completeOT*300

        semi = currentTime.index(':')
        minutes = int(currentTime[:semi])
        seconds = int(currentTime[semi+1:])

        trueElapsed = 300 - (minutes*60 + seconds) + addTime
        trueMin = trueElapsed//60
        trueSec = trueElapsed%60
        trueTime = str(trueMin) + ":" + str(trueSec)
            
    return(trueTime)
    


# inputs soup and file to write, writes game data to file
def writeCSV(soupObject,writeFile,quarter):
    # writing data to csv file
    # ids indicate start of meaningful text
    AS = 0
    HS = 0
    ids = {'1st Quarter Summary','2nd Quarter Summary','3rd Quarter Summary','4th Quarter Summary','1st Overtime Summary','2nd Overtime Summary','3rd Overtime Summary'} 
    flag = 1
    for tr in soupObject.findAll('tr'):
        tds = tr.findAll('td')
        try:
            while flag == 0:
                try:
                    AS,HS = fixScore(tds[2].text)
                    timeLabel = fixTime(tds[0].text,quarter)
                    writeFile.write(timeLabel + "," + tds[1].text + "," + AS + "," + HS + "," + tds[3].text + "\n")
                except IndexError:
                    timeLabel = fixTime(tds[0].text,quarter)
                    writeFile.write(timeLabel + "," + tds[1].text + "\n")
                break
            # find ids in soup, begin writing after that
            if tds[0].text in ids:
                flag = 0
            else:
                pass
        except IndexError:
             pass

    return(AS,HS)

# newID is integer
def insertGameID(oldURL,newID):
    newID = str(newID)
    #find characters for gameID
    ident = 'gameId='
    position = oldURL.index(ident)
    start = position + len(ident)
    stop = oldURL.index('&')
    #insert newID
    newURL = oldURL.replace(oldURL[start:stop],newID)
    return(newURL)

# newPeriod is integer
def changePeriod(oldURL,newPeriod):
    newPeriod = str(newPeriod)
    #identify period character
    ident = 'period='
    position = oldURL.index(ident)
    start = position + len(ident)
    stop = len(oldURL)
    #change period
    newURL = oldURL.replace(oldURL[start:stop],newPeriod)
    return(newURL)


def writeGame(idNum):
    # name by game ID
    fileName = str(idNum) + '.csv'
    f = open(fileName,'w')
    
    
    # genericURL
    genURL = 'http://scores.espn.go.com/nba/playbyplay?gameId=xxxxxxxxx&period=X'
    url = insertGameID(genURL,idNum)
    # need to finish team list
    teams = {'BOS','BKN','NY','PHI','TOR','CHI','CLE','DET','IND','MIL',
             'ATL','CHA','MIA','ORL','WSH','GS','LAC','LAL','PHX','SAC',
             'DAL','HOU','MEM','NO','SA','DEN','MIN','OKC','POR','UTAH',
             'EAST','WEST'}
    matchup = getTeams(url,teams)
    print(matchup[0])
    print(matchup[1])
    f.write("Away" + "," + matchup[0] + "\n")
    f.write("Home" + "," + matchup[1] + "\n")
    f.write("Time" + "," + "awayTeam" + "," + "awayScore" + "," + "homeScore" + "," + "homeTeam" + "\n")
    # write all 4 quarters
    for x in range(1,5):
        pURL = changePeriod(url,x)
        r = requests.get(pURL)
        soup = BeautifulSoup(r.text)
        awayScore,homeScore = writeCSV(soup,f,x)
        time.sleep(0.5)
        print(awayScore)
        print(homeScore)
        print(x)
        
    # account for OT games
    # if final awayScore = homeScore and quarter > 4.. continue
    # try 2OT game
    # 1OT: 
    while(x > 3 and awayScore == homeScore):

        # increment to next quarter
        x = x + 1
        print(x)
        pURL = changePeriod(url,x)
        print(pURL)
        r = requests.get(pURL)
        soup = BeautifulSoup(r.text)
        awayScore,homeScore = writeCSV(soup,f,x)
        print(awayScore)
        print(homeScore)
        
    else:
        pass 
        
    f.close()

# returns away team and home team
def getTeams(theURL,teamList):
    r = requests.get(theURL)
    soup = BeautifulSoup(r.text)
    # away,home
    playing = []
    flag = 0
    for tr in soup.findAll('tr'):
        tds = tr.findAll('td')
        try:
            if tds[0].text in teamList:
                playing.append(tds[0].text)
        except IndexError:
            pass
    return(playing)

def downloadRange(startID,endID):
    start_time = time.time()
    for games in range(startID,endID+1):
        writeGame(games)
        # add delay to be nice to host server
        time.sleep(1.5)

    print(time.time() - start_time)
        
teams = {'BOS','BKN','NY','PHI','TOR','CHI','CLE','DET','IND','MIL',
        'ATL','CHA','MIA','ORL','WSH','GS','LAC','LAL','PHX','SAC',
        'DAL','HOU','MEM','NO','SAS','DEN','MIN','OKC','POR','UTAH',
        'EAST','WEST'}

def getTDS(theURL,ids):
    r = requests.get(theURL)
    soup = BeautifulSoup(r.text)
    flag = 1
    count = 0
    for tr in soup.findAll('tr'):
        tds = tr.findAll('td')
        
        try:
            while flag == 0:
                print(tds[2].text)
                break
            if tds[0].text in ids:
                flag = 0
            else:
                pass
        except IndexError:
             pass

      

            
##url = 'http://scores.espn.go.com/nba/playbyplay?gameId=400277940&period=2'
##url = 'http://scores.espn.go.com/nba/playbyplay?gameId=400488874&period=2'





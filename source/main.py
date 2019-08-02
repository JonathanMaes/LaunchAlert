# -*- coding: utf-8 -*-

import locale
import time
import urllib.request
import webbrowser
import zroya
status = zroya.init(
    app_name="Jonathan's Launch Notifications",
    company_name="OrOrg Development inc.",
    product_name="Launch Alert",
    sub_product="core",
    version="v1.0.0"
)
if not status:
    print("Initialization failed")

from bs4 import BeautifulSoup
from datetime import datetime
from win10toast import ToastNotifier


def checkWebsite(websiteNumber, num=0):
    if websiteNumber == 0:
        url = 'http://rocketlaunch.live'

        try:
            with urllib.request.urlopen(url) as response:
                html_doc = response.read()
            soup = BeautifulSoup(html_doc, 'html.parser')
        except urllib.error.HTTPError:
            return emptyDict()

        nextLaunch = soup.find_all('div', class_='launch')[num] # First <div> with class launch is the next launch div
        details = nextLaunch.find_all('h4', {'itemprop': 'name'})[0].find_all('a')[0] # The div contains an <h4> with an <a> with the sattelite in

        liveLink = None
        if len(nextLaunch.find_all('div', class_='launch_live_embed')) > 0:
            liveFeedDiv = nextLaunch.find_all('div', class_='launch_live_embed')[0] # The div containing the video has class 'launch_live_embed'
            if len(liveFeedDiv.find_all('iframe')) > 0:
                iframe = liveFeedDiv.find_all('iframe')[0] # That div contains an iframe which renders the video
                liveLink = iframe['src'] # The 'src' attribute of that iframe contains the link to the video (often youtube)
        
        try:
            mission = details.text
            detailed_link = url + details['href'] # The <a> links to a detailed page
            timeSinceEpoch = int(nextLaunch['data-sortdate']) # The data-sortdate attribute contains the time since epoch of the launch
            vehicle = nextLaunch.find_all('h4', {'itemprop': 'name'})[1].find_all('a')[0].text # The second <h4> with an <a> tag contains the vehicle
            provider = nextLaunch.find_all('div', class_='rlt-provider')[0].find_all('a')[0].text # The <div> with class 'rlt-provider' contains the launch provider
            location = nextLaunch.find_all('div', class_='rlt-location')[0].text.strip().replace('\n', ', ').replace('\t', '') # The <div> with class 'rlt-location' contains the location
        except: # Something went wrong, render this site useless
            timeSinceEpoch = 1e100
            mission = detailed_link = vehicle = provider = location = None

    elif websiteNumber == 1:
        url = 'https://nextspaceflight.com/launches'

        try:
            with urllib.request.urlopen(url) as response:
                html_doc = response.read()
            soup = BeautifulSoup(html_doc, 'html.parser')
        except urllib.error.HTTPError:
            return emptyDict()

        nextLaunch = soup.find_all('div', class_='demo-card-square')[num] # The first div with class 'demo-card-square' is the first launch

        try:
            links = nextLaunch.find_all('a')
            detailed_link = url + links[0]['href']
            liveLink = links[1]['href'] if len(links) > 1 else None
        except:
            detailed_link = liveLink = None
        
        try:
            vehicleAndMission = nextLaunch.find_all('h5')[0].text.strip().split(' | ') # The h5 in that div is '<vehicle> | <mission>'
            vehicle = vehicleAndMission[0]
            mission = vehicleAndMission[1]
            provider = nextLaunch.find_all('div', class_='mdl-card__title-text')[0].text.strip()
        except:
            vehicle = mission = provider = None

        try:
            details = nextLaunch.find_all('div', class_='mdl-card__supporting-text')[0].text.strip() # Div with this class contains 'time <br/> location'
            locale.setlocale(locale.LC_ALL, 'en_US.utf8') # For correct parsing of US time format to time since epoch
            p = '%a %b %d, %Y %H:%M %Z' # Example that satisfies this format: 'Sat Aug 03, 2019 22:51 UTC' (works with UTC)
            timeString = details.split('\n')[0].strip()
            epoch = datetime(1970, 1, 1)
            timeSinceEpoch = int((datetime.strptime(timeString, p) - epoch).total_seconds())
            location = details.split('\n')[-1].strip()
        except:
            location = None
            timeSinceEpoch = 1e100 # Just a large value so this isnt taken as the actual launch time later on
            # Concidentally, this is also the time of the first liftoff of SLS

    if timeSinceEpoch - time.time() < 0:
        return checkWebsite(websiteNumber, num=num+1)

    return {
        'link' : detailed_link,
        'liveLink' : liveLink,
        'mission' : mission,
        'time' : timeSinceEpoch,
        'rocket' : vehicle,
        'provider' : provider,
        'location' : location
    }


def emptyDict():
    return {
            'link' : None,
            'liveLink' : None,
            'mission' : None,
            'time' : 1e100,
            'rocket' : None,
            'provider' : None,
            'location' : None
        }


def beautifyTime(timeSinceEpoch):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timeSinceEpoch))


def generateSummary(listOfDicts):
    d = {key:[dic[key] for dic in listOfDicts] for key in listOfDicts[0].keys()}

    i = d['time'].index(min([t for t in d['time'] if type(t) == int])) # Number of site which reports the earliest liftoff time
    for link in d['liveLink']: # Give preference to links to youtube
        if link is not None:
            if 'youtube' in link: # Can not check instantly because link can be None, so we need this nested if
                d['liveLink'] = [link]
                break

    return {
        'link' : d['link'][i], # same link as the one with the earliest reported liftoff time, no exception
        'liveLink' : next((x for x in d['liveLink'] if x is not None), ''), # next() returns the first not-None element
        'mission' : d['mission'][i] if d['mission'][i] is not None else next((x for x in d['mission'] if x is not None), ''), # the 2nd argument of next() is the default
        'time' : d['time'][i] if d['time'][i] is not None else next((x for x in d['time'] if x is not None), 0),
        'rocket' : d['rocket'][i] if d['rocket'][i] is not None else next((x for x in d['rocket'] if x is not None), ''),
        'provider' : d['provider'][i] if d['provider'][i] is not None else next((x for x in d['provider'] if x is not None), ''),
        'location' : d['location'][i] if d['location'][i] is not None else next((x for x in d['location'] if x is not None), '')
    }

def onAction(nid, action_id, data):
    '''
        Action 0: Dismiss
        Action 1: More info -> link to data['link']
        Action 2: Watch live -> link to data['liveLink']
    '''
    if action_id == 0: # Dismiss
        return
    if action_id == 1: # More info
        webbrowser.open(data['link'])  # Go to example.com
    if action_id == 2:
        webbrowser.open(data['liveLink'])


def generateTemplate(data, firstLine='Next launch:'):
    template = zroya.Template(zroya.TemplateType.ImageAndText4)
    template.setFirstLine(firstLine)
    if firstLine == 'Next launch:':
        template.setSecondLine('%s (T-%d hours)' % (beautifyTime(data['time']), (data['time']-int(time.time()))//3600))
    else:
        template.setSecondLine('%s' % beautifyTime(data['time']))
    template.setThirdLine('%s (%s) | %s' % (data['rocket'], data['provider'], data['mission']))
    template.setAudio(audio=zroya.Audio.Reminder)
    template.setImage('data/rocket.png')
    template.setAttribution('%s' % data['location'])

    template.addAction("Dismiss")
    template.addAction("More info")
    if data['liveLink']:
        template.addAction("Watch live")
    return template


def main():
    site1 = checkWebsite(0)
    site2 = checkWebsite(1)
    data = generateSummary([site1, site2])
    print(data)

    # On start of the program, display the next launch no matter what
    zroya.show(generateTemplate(data), on_action=lambda nic, action_id: onAction(nic, action_id, data))

    importantTimes = [-1e100, 0, 60, 15*60, 3600, 6*3600, 24*3600, 2*24*3600]
    importantTimeStrings = ['', 'Liftoff!', 'T-1 minute!', 'T-15 minutes.', 'T-1 hour.', 'T-6 hours.', 'T-1 day.', 'Next launch:']

    maximumRecheckTime = 1800

    while True:
        site1 = checkWebsite(0)
        site2 = checkWebsite(1)
        data = generateSummary([site1, site2])
        print(data)

        # See if a next importantTime is in the next 1800 seconds, otherwise wait 1800 seconds
        # If a next importantTime is in the next 1800 seconds, then only wait that long, and then after that
        #  re-show the notification with the corresponding importantTimeString

        currentTime = int(time.time())+1
        nextImportantTime = [t for t in importantTimes if data['time']-currentTime > t][-1]
        untilNextTime = (data['time'] - currentTime) - nextImportantTime

        if untilNextTime < maximumRecheckTime:
            time.sleep(untilNextTime)

            firstLine = importantTimeStrings[importantTimes.index(nextImportantTime)]
            zroya.show(generateTemplate(data, firstLine=firstLine), on_action=lambda nic, action_id: onAction(nic, action_id, data))
        else:
            time.sleep(maximumRecheckTime)
        # break


if __name__ == "__main__":
    main()
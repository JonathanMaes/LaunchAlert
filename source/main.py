# -*- coding: utf-8 -*-

# Ideas:
# Stop using zroya and use an actual window without border (self.overrideredirect=True in tkinter App)

import difflib
import locale
import math
import time
import tkinter as tk
import traceback
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


class Launch:
    '''
        @param time (int): Time since epoch of expected liftoff time, math.inf
            if this time is not (yet) exactly known.
        @param rocket (str): Name of the rocket.
        @param mission (str): Name of the sattelite to be launched, or of the entire mission.
        @param provider (str): Name of the launch provider.
        @param link (str)[None]: Link to more detailed information.
        @param liveLink (str)[None]: Link to the live webcast, if available.
        @param location (str)[None]: Location of the launch.
    '''
    importantTimes = [0, 60, 15*60, 3600, 6*3600, 24*3600, 2*24*3600]

    def __init__(self, time, rocket, mission, provider, link=None, liveLink=None, location=None):
        self.time = time
        self.rocket = rocket
        self.mission = mission
        self.provider = provider
        self.link = link
        self.liveLink = liveLink
        self.location = location
    
    def __eq__(self, other):
        b = self.time == other.time
        b &= self.rocket == other.rocket
        b &= self.mission == other.mission
        b &= self.provider == other.provider
        # Links may be different, allowing an update of these links.
        b &= self.location == other.location
        return b
    
    def timeLeft(self):
        ''' @return (int): The amount of seconds until launch. '''
        return self.time - time.time()
    
    def nextImportantTime(self, sinceEpoch=True):
        ''' 
            @param sinceEpoch (bool) [True]: Switch for the return value.
            @return (int): Time since epoch for the next important time if
                sinceEpoch=True, otherwise the number of seconds until liftoff
                that the important time represents.
        '''
        timeLeft = self.timeLeft()
        if sinceEpoch:
            return [self.time - time for time in Launch.importantTimes if time < timeLeft][-1] # Time since epoch for important times still to come
        else:
            return [time for time in Launch.importantTimes if time < timeLeft][-1] # Next member of importantTimes that will be reached

    
    @staticmethod
    def beautifySeconds(s):
        '''
            @param s (int): The amount of seconds until/since liftoff.
            @return (str): Beautified string denoting the time until/since
                liftoff (T+ or T- seconds, minutes, hours, days...).
        '''
        if s == 0:
            return 'Liftoff!'
        else:
            operator = '-' if s > 0 else '+'
            s = abs(s)
            if s <= 60: # 60 seconds or less
                return 'T%s%d second%s.' % (operator, s, '' if s==1 else 's')
            elif s <= 3600: # 60 minutes or less
                m = s//60
                return 'T%s%d minute%s.' % (operator, m, '' if m==1 else 's')
            elif s <= 86400*2: # 48 hours and lower
                h = s//3600
                return 'T%s%d hour%s.' % (operator, h, '' if h==1 else 's')
            else: # Strictly more than 2 days
                d = s//86400
                return 'T%s%d day%s.' % (operator, d, '' if d==1 else 's')
    
    @staticmethod
    def empty():
        '''
            @return (Launch): A launch with as little information as possible.
        '''
        return Launch(math.inf, None, None, None)

# class Popupwindow(tk.Toplevel):
#     def __init__(self):
#         root = tk.Tk()
#         root.withdraw()
#         super().__init__(root)
#         self.overrideredirect(True)
    
#     def display(self):
#         for _ in range(10):
#             self.update()
#             time.sleep(0.5)
#         self.withdraw()

def checkWebsites():
    '''
        @return (list2D): List of lists, with each list containing all
            launches from a certain website.
    '''
    allLaunches = []

    # First website
    url = 'http://rocketlaunch.live'

    try:
        with urllib.request.urlopen(url) as response:
            html_doc = response.read()
        soup = BeautifulSoup(html_doc, 'html.parser')

        launchesDiv = soup.find_all('div', class_='launch')
        launchesList = []
        for nextLaunch in launchesDiv:
            try:
                details = nextLaunch.find_all('div', class_='mission_name')[0].find_all('h4')[0].find_all('a')[0] # The div contains an <h4> with an <a> with the sattelite in

                liveLink = None
                if len(nextLaunch.find_all('div', class_='launch_live_embed')) > 0:
                    liveFeedDiv = nextLaunch.find_all('div', class_='launch_live_embed')[0] # The div containing the video has class 'launch_live_embed'
                    if len(liveFeedDiv.find_all('iframe')) > 0:
                        iframe = liveFeedDiv.find_all('iframe')[0] # That div contains an iframe which renders the video
                        liveLink = iframe['src'] # The 'src' attribute of that iframe contains the link to the video (often youtube)
                
                mission = details.text
                detailed_link = url + details['href'] # The <a> links to a detailed page

                timeSinceEpoch = int(nextLaunch['data-sortdate']) # The data-sortdate attribute contains the time since epoch of the launch
                if timeSinceEpoch%86400 >= 86397: # This means the date is known up to month (97), quartal (98) or year (99)
                    timeSinceEpoch = math.inf # Do not use this to post notifications because the time is not known

                rocket = nextLaunch.find_all('div', class_='rlt-vehicle')[0].find_all('a')[0].text
                provider = nextLaunch.find_all('div', class_='rlt-provider')[0].find_all('a')[0].text
                location = nextLaunch.find_all('div', class_='rlt-location')[0].text.strip().replace('\n', ', ').replace('\t', '') # <div> has more text than just one line
                
                launchesList.append(Launch(timeSinceEpoch, rocket, mission, provider, link=detailed_link, liveLink=liveLink, location=location))
            except:
                print('%s: Error while parsing HTML structure:\n%s' % (url, traceback.format_exc()))

        allLaunches.append(sorted(launchesList, key=lambda l:l.time))
    except urllib.error.HTTPError:
        print('%s: could not connect to website.' % (url))


    # Second website
    url = 'https://nextspaceflight.com/launches'

    try:
        with urllib.request.urlopen(url) as response:
            html_doc = response.read()
        soup = BeautifulSoup(html_doc, 'html.parser')

        launchesDiv = soup.find_all('div', class_='demo-card-square')
        launchesList = []
        for nextLaunch in launchesDiv:
            try:
                links = nextLaunch.find_all('a')
                detailed_link = url + links[0]['href']
                liveLink = links[1]['href'] if len(links) > 1 else None
            
                rocketAndMission = nextLaunch.find_all('h5')[0].text.strip().split(' | ') # The h5 in that div is '<rocket> | <mission>'
                rocket = rocketAndMission[0]
                mission = rocketAndMission[1]
                provider = nextLaunch.find_all('div', class_='mdl-card__title-text')[0].text.strip()

                details = nextLaunch.find_all('div', class_='mdl-card__supporting-text')[0].text.strip() # Div with this class contains 'time <br/> location'
                location = details.split('\n')[-1].strip()
                if details.startswith('NET'):
                    timeSinceEpoch = math.inf # If the exact time is not known (NET), then don't notify this launch
                else:
                    locale.setlocale(locale.LC_ALL, 'en_US.utf8') # For correct parsing of US time format to time since epoch
                    p = '%a %b %d, %Y %H:%M %Z' # Example that satisfies this format: 'Sat Aug 03, 2019 22:51 UTC' (works with UTC)
                    timeString = details.split('\n')[0].strip()
                    epoch = datetime(1970, 1, 1)
                    timeSinceEpoch = int((datetime.strptime(timeString, p) - epoch).total_seconds())
                
                launchesList.append(Launch(timeSinceEpoch, rocket, mission, provider, link=detailed_link, liveLink=liveLink, location=location))
            except:
                print('%s: Error while parsing HTML structure:\n%s' % (url, traceback.format_exc()))
            
        allLaunches.append(sorted(launchesList, key=lambda l:l.time))
    except urllib.error.HTTPError:
        print('%s: could not connect to website.' % (url))

    return allLaunches


def beautifyTime(timeSinceEpoch):
    '''
        @param timeSinceEpoch (int): The time since the epoch.
        @return (str): The beautified time string in the format 
            'YYYY-MM-DD HH:MM:SS'
    '''
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timeSinceEpoch))


def generateSummary(listOfLists):
    '''
        @param listOfLists (list2D): List of lists, with each list containing
            all launches from a certain website.
        @return (list): List of Launch objects, summarizing all information
            from the different websites for each respective launch.
    '''
    n = len([1 for l in listOfLists if len(l) != 0]) # So if a website errors the entire time,
    threshold = math.ceil(n*0.4)
    maxTimeDifference = 60

    allLaunches = sorted([item for sublist in listOfLists for item in sublist], key=lambda x:x.time)
    
    launches = []
    for launch in allLaunches:
        # If the time of launch is math.inf, or a launch within a minute of this one has already been found, then ignore this one
        if launch.time == math.inf or any(abs(l.time - launch.time) < maxTimeDifference for l in launches):
            continue
        # Get all launches that are within a minute of this one
        similarLaunches = [l for l in allLaunches if abs(l.time - launch.time) < maxTimeDifference]
        # If not more than 40% of all websites report this time, ignore it
        if len(similarLaunches) < threshold:
            continue
        
        # Summarize all these similar launches
        # Use difflib.get_close_matches to standardize the rocket
        ## Time of launch: the lowest of them all, as to not to miss it
        time = min([l.time for l in similarLaunches])
        time_i = [l.time for l in similarLaunches].index(time) # Number of site which reports the earliest liftoff time
        ## Rocket
        rocket = max([l.rocket for l in similarLaunches], key=len) # The longer the name of the rocket, the more specific, probably
        rocket_i = [l.rocket for l in similarLaunches].index(rocket) # Number of site which uses this rocket name
        ## Mission
        mission = [l.mission for l in similarLaunches][rocket_i]
        ## Provider
        provider = [l.provider for l in similarLaunches][rocket_i]
        ## Link
        link = [l.link for l in similarLaunches][time_i] # Go to the website that reports the earliest liftoff time

        ## LiveLink
        liveLink = None
        for live in [l.liveLink for l in similarLaunches]: # Give preference to links to youtube
            if live is not None:
                if 'youtube' in live: # Can not check instantly for youtube because link can be None, so we need this nested if
                    liveLink = live
                    break

        ## Location
        location = [l.location for l in similarLaunches][time_i]
        if location is None: # If the location that site shows is None, then take another one that is not None, if possible
            location = next((l.location for l in similarLaunches if l.location is not None), None)

        launches.append(Launch(time, rocket, mission, provider, link=link, liveLink=liveLink, location=location))
    return sorted(launches, key=lambda l:l.time)


def onAction(nid, action_id, launch):
    '''
        Action 0: Dismiss
        Action 1: More info -> link to launch.link
        Action 2: Watch live -> link to launch.livelink
    '''
    if action_id == 0: # Dismiss
        return
    if action_id == 1: # More info
        webbrowser.open(launch.link)  # Go to example.com
    if action_id == 2:
        webbrowser.open(launch.livelink)


def generateTemplate(launch, closestImportantTime=True):
    '''
        @param launch (Launch): The launch which this notification is for.
        @param closestImportantTime (bool) [True]: If true, the header of the
            notification is taken to be the next important time (24 hours, 
            60 minutes...), if false, the real time to liftoff is taken.
            (This is to make sure the notification doesn't say T-23 hours just
            because the notification is one second late for T-24 hours.)
        @return (zroya.Template): The template for the resulting notification.
    '''
    template = zroya.Template(zroya.TemplateType.ImageAndText4)
    if closestImportantTime:
        template.setFirstLine('%s' % Launch.beautifySeconds(launch.nextImportantTime(sinceEpoch=False)))
    else:
        template.setFirstLine('%s' % Launch.beautifySeconds(launch.time - time.time()))
    template.setSecondLine('%s' % beautifyTime(launch.time))
    template.setThirdLine('%s (%s) | %s' % (launch.rocket, launch.provider, launch.mission))
    template.setAudio(audio=zroya.Audio.Reminder)
    template.setImage('data/rocket.png')
    if launch.location is not None:
        template.setAttribution('%s' % launch.location)

    template.addAction("Dismiss")
    template.addAction("More info")
    if launch.liveLink is not None:
        template.addAction("Watch live")
    
    return template


def main():
    allLaunches = generateSummary(checkWebsites())

    # On start of the program, display the next launch no matter what
    zroya.show(generateTemplate(allLaunches[0], closestImportantTime=False), on_action=lambda nic, action_id: onAction(nic, action_id, allLaunches[0]))

    maximumRecheckTime = 1800
    while True:
        nextImportantLaunch = sorted(allLaunches, key=lambda l:l.nextImportantTime(sinceEpoch=True))[0]

        # Next important time
        nextImportantTimeEpoch = nextImportantLaunch.nextImportantTime(sinceEpoch=True)
        untilNextTime = nextImportantTimeEpoch - math.ceil(time.time())

        # Wait appropriately
        if untilNextTime < maximumRecheckTime:
            while time.time() < nextImportantTimeEpoch: # To prevent unwanted waiting (because of time.sleep) after sleep mode etc.
                time.sleep(1)
        else:
            nextRecheckTime = time.time() + maximumRecheckTime
            while time.time() < nextRecheckTime: # To prevent unwanted waiting (because of time.sleep) after sleep mode etc.
                time.sleep(1)

        # Check whether the launch still exists, otherwise check the next
        # important time again (i.e., continue the next iteration of the loop)
        allLaunches = generateSummary(checkWebsites())
        if untilNextTime < maximumRecheckTime: # If the next important time was within the maximumRecheckTime interval (same condition as before)
            if nextImportantLaunch in allLaunches:
                # Update with new information that isn't included in the Launch.__eq__ equality operator (e.g. liveLink)
                nextImportantLaunch = [l for l in allLaunches if nextImportantLaunch == l][0]
                zroya.show(generateTemplate(nextImportantLaunch), on_action=lambda nic, action_id: onAction(nic, action_id, nextImportantLaunch))


if __name__ == "__main__":
    main()

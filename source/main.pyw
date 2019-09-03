# -*- coding: utf-8 -*-

# Ideas:
# Stop using zroya and use an actual window without border (self.overrideredirect=True in tkinter App)
# Collapse launcher and company names to closest result with difflib.get_close_matches()

import ctypes
# import difflib
import locale
import math
import os
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
    reportError(fatal=True, message='Initialization failed.')

from bs4 import BeautifulSoup
from datetime import datetime


class Launch:
    '''
        @param time (int): Time since epoch of expected liftoff time, math.inf
            if this time is not (yet) exactly known.
        @param launcher (str): Name of the launcher.
        @param mission (str): Name of the sattelite to be launched, or of the entire mission.
        @param provider (str): Name of the launch provider.
        @param link (str)[None]: Link to more detailed information.
        @param liveLink (str)[None]: Link to the live webcast, if available.
        @param location (str)[None]: Location of the launch.
    '''
    importantTimes = [-math.inf, 0, 60, 5*60, 15*60, 3600, 6*3600, 24*3600, 2*24*3600]

    def __init__(self, t, launcher, mission, provider, link=None, liveLink=None, location=None):
        self.time = t
        self.launcher = launcher
        self.mission = mission
        self.provider = provider
        self.link = link
        self.liveLink = liveLink
        self.location = location
    
    def __eq__(self, other):
        b = self.time == other.time
        b &= self.launcher == other.launcher
        b &= self.mission == other.mission
        b &= self.provider == other.provider
        # Links may be different, allowing an update of these links.
        b &= self.location == other.location
        return b
    
    def __str__(self):
        return '%s | %s (%s)' % (Launch.beautifyTime(self.time), self.launcher, self.mission)
    
    def __repr__(self):
        return "Launch(%r, %r, %r, %r, link=%r, liveLink=%r, location=%r)" % (self.time, self.launcher, self.mission, self.provider, self.link, self.liveLink, self.location)

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
            return [self.time - t for t in Launch.importantTimes if t < timeLeft][-1] # Time since epoch for important times still to come
        else:
            return [t for t in Launch.importantTimes if t < timeLeft][-1] # Next member of importantTimes that will be reached

    
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
    def beautifyTime(timeSinceEpoch):
        '''
            @param timeSinceEpoch (int): The time since the epoch.
            @return (str): The beautified time string in the format 
                'YYYY-MM-DD HH:MM:SS'
        '''
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timeSinceEpoch))

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

    loadedWebsite = False
    try:
        with urllib.request.urlopen(url) as response:
            html_doc = response.read()
        soup = BeautifulSoup(html_doc, 'html.parser')
        loadedWebsite = True
    except:
        reportError(fatal=False, message='%s: could not connect to website.' % url)

    if loadedWebsite:
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

                launcher = nextLaunch.find_all('div', class_='rlt-vehicle')[0].find_all('a')[0].text
                provider = nextLaunch.find_all('div', class_='rlt-provider')[0].find_all('a')[0].text
                location = nextLaunch.find_all('div', class_='rlt-location')[0].text.strip().replace('\n', ', ').replace('\t', '') # <div> has more text than just one line
                
                launchesList.append(Launch(timeSinceEpoch, launcher, mission, provider, link=detailed_link, liveLink=liveLink, location=location))
            except:
                reportError(fatal=False, message='%s: Error while parsing HTML structure.' % url)

        allLaunches.append(sorted(launchesList, key=lambda l:l.time))


    # Second website
    url = 'https://nextspaceflight.com/launches'

    loadedWebsite = False
    try:
        with urllib.request.urlopen(url) as response:
            html_doc = response.read()
        soup = BeautifulSoup(html_doc, 'html.parser')
        loadedWebsite = True
    except:
        reportError(fatal=False, message='%s: could not connect to website.' % url)

    if loadedWebsite:
        launchesDiv = soup.find_all('div', class_='demo-card-square')
        launchesList = []
        for nextLaunch in launchesDiv:
            try:
                links = nextLaunch.find_all('a')
                detailed_link = os.path.dirname(url) + links[0]['href']
                liveLink = links[1]['href'] if len(links) > 1 else None
            
                launcherAndMission = nextLaunch.find_all('h5')[0].text.strip().split(' | ') # The h5 in that div is '<launcher> | <mission>'
                launcher = launcherAndMission[0]
                mission = launcherAndMission[1]
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
                
                launchesList.append(Launch(timeSinceEpoch, launcher, mission, provider, link=detailed_link, liveLink=liveLink, location=location))
            except:
                reportError(fatal=False, message='%s: Error while parsing HTML structure.' % url)
            
        allLaunches.append(sorted(launchesList, key=lambda l:l.time))

    return allLaunches


def reportError(fatal=False, message=''):
    exc = '\t' + traceback.format_exc().replace('\n', '\n\t')
    message = '\n%s' % message

    if fatal:
        info = u"A fatal error occured:%s\n\n%s\n\nYou have to manually restart the program." % (message, exc)
    else:
        info = u"An non-fatal error occured:%s\n\n%s\n\nThe program has dealt with the error and continues to run correctly." % (message, exc)

    ctypes.windll.user32.MessageBoxW(0, info, u"Jonathan's Launch Notifications", 0)

    if fatal:
        quit()


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
        # If the time of launch is math.inf, or the launch has passed, or a launch within a minute of this one has already been found, then ignore this one
        if launch.time == math.inf or launch.time < time.time() or any(abs(l.time - launch.time) < maxTimeDifference for l in launches):
            continue
        # Get all launches that are within a minute of this one
        similarLaunches = [l for l in allLaunches if abs(l.time - launch.time) < maxTimeDifference]
        # If not more than 40% of all websites report this time, ignore it
        if len(similarLaunches) < threshold:
            continue
        
        # Summarize all these similar launches
        # Use difflib.get_close_matches to standardize the launcher
        ## Time of launch: the lowest of them all, as to not to miss it
        t = min([l.time for l in similarLaunches])
        time_i = [l.time for l in similarLaunches].index(t) # Number of site which reports the earliest liftoff time
        ## Launcher
        launcher = max([l.launcher for l in similarLaunches], key=len) # The longer the name of the launcher, the more specific, probably
        launcher_i = [l.launcher for l in similarLaunches].index(launcher) # Number of site which uses this launcher name
        ## Mission
        mission = [l.mission for l in similarLaunches][launcher_i]
        ## Provider
        provider = [l.provider for l in similarLaunches][launcher_i]
        ## Link
        link = [l.link for l in similarLaunches][time_i] # Go to the website that reports the earliest liftoff time

        ## LiveLink
        liveLink = None
        for keyword in ['spacex', 'rocketlab', 'youtube']: # First look for the first element, then the next... (most specific first)
            for live in [l.liveLink for l in similarLaunches if l.liveLink is not None]: # Give preference to links to known sites
                if keyword in live:
                    liveLink = live
                    break
            if liveLink is not None: # To escape this loop as well
                break
        if liveLink is None: # If no keywords were found
            notNoneLinks = [l.liveLink for l in similarLaunches if l.liveLink is not None]
            if any(notNoneLinks):
                liveLink = notNoneLinks[0]

        ## Location
        location = [l.location for l in similarLaunches][time_i]
        if location is None: # If the location that site shows is None, then take another one that is not None, if possible
            location = next((l.location for l in similarLaunches if l.location is not None), None)

        launches.append(Launch(t, launcher, mission, provider, link=link, liveLink=liveLink, location=location))
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
        webbrowser.open(launch.liveLink)


def notification(launch, closestImportantTime=True):
    '''
        @param launch (Launch): The launch which this notification is for.
        @param closestImportantTime (bool) [True]: If true, the header of the
            notification is taken to be the next important time (24 hours, 
            60 minutes...), if false, the real time to liftoff is taken.
            (This is to make sure the notification doesn't say T-23 hours just
            because the notification is one second late for T-24 hours.)
    '''
    template = zroya.Template(zroya.TemplateType.ImageAndText4)
    if closestImportantTime:
        template.setFirstLine('%s' % Launch.beautifySeconds([t for t in Launch.importantTimes if t > launch.time - time.time()][0]))
    else:
        template.setFirstLine('%s' % Launch.beautifySeconds(launch.time - time.time()))
    template.setSecondLine('%s' % Launch.beautifyTime(launch.time))
    template.setThirdLine('%s (%s) | %s' % (launch.launcher, launch.provider, launch.mission))
    template.setAudio(audio=zroya.Audio.Reminder)
    template.setImage('data/rocket.png')
    if launch.location is not None:
        template.setAttribution('%s' % launch.location)

    template.addAction("Dismiss")
    template.addAction("More info")
    if launch.liveLink is not None:
        template.addAction("Watch live")
    
    zroya.show(template, on_action=lambda nic, action_id: onAction(nic, action_id, launch))


def main():
    allLaunches = generateSummary(checkWebsites())

    # On start of the program, display the next launch no matter what
    notification(allLaunches[0], closestImportantTime=False)

    maximumRecheckTime = 1800
    while True:
        slept = False
        if len(allLaunches) == 0: # No websites could be reached, or no launches are available
            time.sleep(maximumRecheckTime) # Wait before rechecking the websites
            allLaunches = generateSummary(checkWebsites()) # Recheck for allLaunches
            continue # Continue with the next iteration of the loop

        nextImportantLaunch = sorted(allLaunches, key=lambda l:l.nextImportantTime(sinceEpoch=True))[0]
        print(sorted(allLaunches, key=lambda l:l.nextImportantTime(sinceEpoch=True))[:5])

        # Next important time
        nextImportantTimeEpoch = nextImportantLaunch.nextImportantTime(sinceEpoch=True)
        untilNextTime = nextImportantTimeEpoch - math.ceil(time.time())
        nextRecheckTime = min(time.time() + maximumRecheckTime, nextImportantTimeEpoch) # Time since epoch until which we sleep

        # Wait appropriately
        while time.time() < nextRecheckTime: # To prevent unwanted waiting (because of time.sleep) after sleep mode etc.
            time.sleep(1)

        if abs(time.time() - nextRecheckTime) > 10: # True if the program slept too long for the nextImportantTime (e.g. screensaver etc.)
            slept = True
            # Connection to websites not possible instantly after coming out of sleep mode, try in one minute instead
            time.sleep(60) 
        
        # Check whether the launch still exists, otherwise check the next
        # important time again (i.e., continue the next iteration of the loop)
        allLaunches = generateSummary(checkWebsites())
        if nextImportantLaunch in allLaunches:
            nextImportantLaunch = [l for l in allLaunches if nextImportantLaunch == l][0]
            if slept and time.time() > nextImportantTimeEpoch:
                # Notification with current T- time if an importantTime was missed (and the launch hasn't happened yet, otherwise it's pretty useless to push notifications)
                notification(nextImportantLaunch, closestImportantTime=False)

            elif untilNextTime < maximumRecheckTime: # If the time.sleep was ended because an importantTime is now
                # Notification as usual
                notification(nextImportantLaunch)
        
        
if __name__ == "__main__":
    try:
        main()
    except:
        # Something horrible happened, otherwise we would already have caught the error
        reportError(fatal=True)

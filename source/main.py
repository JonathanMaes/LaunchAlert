# -*- coding: utf-8 -*-

import locale
import time
import urllib.request
import zroya

from bs4 import BeautifulSoup
from datetime import datetime
from win10toast import ToastNotifier


def checkWebsite(num):
    if num == 0:
        url = 'http://rocketlaunch.live'
        with urllib.request.urlopen(url) as response:
            html_doc = response.read()
        soup = BeautifulSoup(html_doc, 'html.parser')

        nextLaunch = soup.find_all('div', class_='launch')[0] # First <div> with class launch is the next launch div

        liveLink = None
        
        liveFeedDiv = nextLaunch.find_all('div', class_='launch_live_embed')[0] # The div containing the video has class 'launch_live_embed'
        if len(liveFeedDiv.find_all('iframe')) > 0:
            iframe = liveFeedDiv.find_all('iframe')[0] # That div contains an iframe which renders the video
            liveLink = iframe['src'] # The 'src' attribute of that iframe contains the link to the video (often youtube)
        timeSinceEpoch = int(nextLaunch['data-sortdate']) # The data-sortdate attribute contains the time since epoch of the launch
        details = nextLaunch.find_all('h4', {'itemprop': 'name'})[0].find_all('a')[0] # The div contains an <h4> with an <a> with the sattelite in
        
        mission = details.text
        detailed_link = url + details['href'] # The <a> links to a detailed page
        vehicle = nextLaunch.find_all('h4', {'itemprop': 'name'})[1].find_all('a')[0].text # The second <h4> with an <a> tag contains the vehicle
        provider = nextLaunch.find_all('div', class_='rlt-provider')[0].find_all('a')[0].text # The <div> with class 'rlt-provider' contains the launch provider
        location = nextLaunch.find_all('div', class_='rlt-location')[0].text.strip().replace('\n', ', ').replace('\t', '') # The <div> with class 'rlt-location' contains the location

        return {
            'link' : detailed_link,
            'liveLink' : liveLink,
            'mission' : mission,
            'time' : timeSinceEpoch,
            'rocket' : vehicle,
            'provider' : provider,
            'location' : location
        }

    elif num == 1:
        url = 'https://nextspaceflight.com'

        with urllib.request.urlopen(url) as response:
            html_doc = response.read()
        soup = BeautifulSoup(html_doc, 'html.parser')

        nextLaunch = soup.find_all('div', class_='demo-card-square')[0] # The first div with class 'demo-card-square' is the first launch

        details = nextLaunch.find_all('div', class_='mdl-card__supporting-text')[0].text.strip() # Div with this class contains 'time <br/> location'
        links = nextLaunch.find_all('a')

        detailed_link = url + links[0]['href']
        liveLink = links[1]['href'] if len(links) > 1 else None
        
        vehicleAndMission = nextLaunch.find_all('h5')[0].text.strip().split(' | ') # The h5 in that div is '<vehicle> | <mission>'
        vehicle = vehicleAndMission[0]
        mission = vehicleAndMission[1]
        provider = nextLaunch.find_all('div', class_='mdl-card__title-text')[0].text.strip()

        locale.setlocale(locale.LC_ALL, 'en_US.utf8') # For correct parsing of US time format to time since epoch
        p = '%a %b %d, %Y %H:%M %Z' # Example that satisfies this format: 'Sat Aug 03, 2019 22:51 UTC' (works with UTC)
        timeString = details.split('\n')[0].strip()
        epoch = datetime(1970, 1, 1)
        timeSinceEpoch = int((datetime.strptime(timeString, p) - epoch).total_seconds())

        location = details.split('\n')[-1].strip()
        
        return {
            'link' : detailed_link,
            'liveLink' : liveLink,
            'mission' : mission,
            'time' : timeSinceEpoch,
            'rocket' : vehicle,
            'provider' : provider,
            'location' : location
        }


def beautifyTime(timeSinceEpoch):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timeSinceEpoch))


def generateSummary(listOfDicts):
    dictOfLists = {key:[d[key] for d in listOfDicts] for key, _ in listOfDicts[0].items()}

    lowestTimeIndex = dictOfLists['time'].index(min(dictOfLists['time'])) # Number of site which reports the earliest liftoff time
    trustedLinks = [i for i in dictOfLists['liveLink'] if any(c in i for c in ('youtube', 'spacex'))] # Give preference to links to youtube
    if len(trustedLinks) != 0:
        dictOfLists['liveLink'] = trustedLinks

    return {
        'link' : dictOfLists['link'][lowestTimeIndex], # same link as the one with the earliest reported liftoff time
        'liveLink' : next((item for item in dictOfLists['liveLink'] if item is not None), ''), # next() returns the first not-None element
        'mission' : next((item for item in dictOfLists['mission'] if item is not None), ''), # the 2nd argument of next() is the default
        'time' : dictOfLists['time'][lowestTimeIndex],
        'rocket' : dictOfLists['rocket'][lowestTimeIndex],
        'provider' : dictOfLists['provider'][lowestTimeIndex],
        'location' : dictOfLists['location'][lowestTimeIndex]
    }


def main():
    site1 = checkWebsite(0)
    site2 = checkWebsite(1)

    print(site1)
    print(site2)
    print(generateSummary([site1, site2]))



    template = zroya.Template(zroya.TemplateType.Text4)
    template.setFirstLine('Launch alert!')
    template.setSecondLine('%s | %s' % ('rocket', 'mission'))
    template.setThirdLine('%s')


main()
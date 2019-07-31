# -*- coding: utf-8 -*-

import time
import urllib.request

from bs4 import BeautifulSoup
from win10toast import ToastNotifier


def checkWebsite(url):
    if url == 'http://rocketlaunch.live/':
        with urllib.request.urlopen('http://rocketlaunch.live/') as response:
            html_doc = response.read()
        soup = BeautifulSoup(html_doc, 'html.parser')

        nextLaunch = soup.find_all('div', class_='launch')[0] # First <div> with class launch is the next launch div
        timeSinceEpoch = nextLaunch['data-sortdate'] # The data-sortdate attribute contains the time since epoch of the launch
        details = nextLaunch.find_all('h4', {'itemprop': 'name'})[0].find_all('a')[0] # The div contains an <h4> with an <a> with the sattelite in
        
        mission = details.text
        detailed_link = 'http://rocketlaunch.live' + details['href'] # The <a> links to a detailed page
        vehicle = nextLaunch.find_all('h4', {'itemprop': 'name'})[1].find_all('a')[0].text # The second <h4> with an <a> tag contains the vehicle
        provider = nextLaunch.find_all('div', class_='rlt-provider')[0].find_all('a')[0].text # The <div> with class 'rlt-provider' contains the launch provider
        location = nextLaunch.find_all('div', class_='rlt-location')[0].text.strip().replace('\n', ', ') # The <div> with class 'rlt-location' contains the location

        return {
            'link' : detailed_link,
            'mission' : mission, # the <a> tag that is details has as text the mission title
            'time' : timeSinceEpoch,
            'timeString' : time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(timeSinceEpoch))),
            'rocket' : vehicle,
            'provider' : provider,
            'location' : location
        }


def main():
    site1 = checkWebsite('http://rocketlaunch.live/')
    toaster = ToastNotifier()
    toaster.show_toast("Sample Notification","Python is awesome!!!")


print(checkWebsite('http://rocketlaunch.live/'))
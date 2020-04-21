import ctypes
import psutil
import sys
import traceback
import urllib.request
import webbrowser
from packaging import version as pkg_version


## PROGRAM ENVIRONMENT VARIABLES ##
PROGRAMNAME = u"Jonathan's Launch Notifications"
PROGRAMNAMEEXECUTABLE = u"jonathanslaunchnotifications"
COMPANYNAME = u"OrOrg Development inc."
REMOTE_FILENAME_CHANGELOG = 'https://raw.githubusercontent.com/JonathanMaes/LaunchAlert/master/source/changelog.txt'
REMOTE_FILENAME_INSTALLER = 'https://github.com/JonathanMaes/LaunchAlert/blob/master/installer/JonathansLaunchAlert_installer.exe?raw=true'


## PROGRAM ENVIRONMENT FUNCTIONS ##
def reportError(fatal=False, notify=None, message=''):
    if notify is None:
        notify = fatal

    exc = '\t' + traceback.format_exc().replace('\n', '\n\t')
    message = '\n%s' % message

    if fatal:
        info = u"A fatal error occured: %s\n\n%s\n\nYou have to manually restart the program." % (message, exc)
    else:
        info = u"An non-fatal error occured: %s\n\n%s\n\nThe program has dealt with the error and continues to run correctly." % (message, exc)
    
    if notify:
        ctypes.windll.user32.MessageBoxW(0, info, PROGRAMNAME, 0)

    if fatal:
        sys.exit()

def checkForUpdates(versionFile=REMOTE_FILENAME_CHANGELOG):
    '''
        @param versionFile (string): The URL where the production changelog is located.
        @return (bool): Whether a new update will be installed or not.
    '''
    # Read the file, and extract the remote version number, which is located at the top of versionFile
    try:
        with urllib.request.urlopen(versionFile) as changelog:
            version_remote = changelog.readline().strip().decode("utf-8")
        with open('changelog.txt', 'r') as f:
            version_local = f.readline().strip()
        
        shouldUpdate = pkg_version.parse(version_local) < pkg_version.parse(version_remote)
        if shouldUpdate:
            text = "An update for %s has been found.\nDo you wish to install it now?" % PROGRAMNAME
            title = "%s Updater" % PROGRAMNAME
            result = ctypes.windll.user32.MessageBoxW(0, text, title, 4) # 4: 'Yes'/'No'-messagebox
            if result == 6: # 'Yes'
                webbrowser.open(REMOTE_FILENAME_INSTALLER)
                return True
            elif result == 7: # 'No'
                return False
            else:
                reportError(fatal=False, notify=True, message='Unknown return code in the updater messagebox.')
                return False
    except:
        reportError(fatal=False, notify=False, message='%s: could not connect to update-server.' % versionFile)
        return False

def checkIfRunning(shutOtherDown=True):
    instances = []
    for proc in psutil.process_iter():
        try:
            pinfo = proc.as_dict(attrs=['pid', 'name', 'create_time'])
            if PROGRAMNAMEEXECUTABLE.lower() in pinfo['name'].lower():
                instances.append(pinfo)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    sorted_instances = sorted(instances, key=lambda x:x['create_time'])
    for elem in sorted_instances[:-1]: # All but the last one opened
        if shutOtherDown:
            psutil.Process(int(elem['pid'])).terminate() # Kill other processes
            print('Program was already running, terminated previous instance.')
        else:
            print('WARNING: Multiple instances of the program are running.')
    
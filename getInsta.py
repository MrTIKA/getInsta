#!/Library/Frameworks/Python.framework/Versions/3.6/bin/python3

import pickle
import argparse
import requests
import subprocess
from time import sleep

import selenium.webdriver as webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options

#TODO:
#Make configration file for pickle locations

def createDriver(headless=True):
    '''
        created a global cromedriver to be used for getting posts
        arguments: headless: bool - if set to true, the chorme window will not open and operate in the backround
    '''

    global driver
    chrome_options = Options()

    if headless:
        verboseprint("Chrome is set to headless mode")
        chrome_options.add_argument("--headless")
    driver = webdriver.Chrome("/users/tayfunturanligil/Documents/chromedriver",chrome_options=chrome_options)

def logIn():
    '''
        load the cookies or handle login for the defaulth account, or secondary account
        arguments: ttikat: bool - if set to true, it will log in as that account
    '''

    #Driver has to have done something before we can load cookies, so I ust call google
    driver.get('https://www.google.com')

    #this path will work on any OS and added for github. 
	#In my computer I hard coded my path for simlicity
    cookiePath = pathlib.Path(__file__).parent / 'getInstaCookies.pkl'

    try:
    	cookies = pickle.load(open("/users/tayfunturanligil/Documents/getInstaTtikatCookies.pkl", "rb"))

    except Exception as e:
        print('Failed to find cookie pickle, will create a new one')
        print(e)

        username = input("Instagram username: ")
        password = getpass("Password (will not show when typing):")

        driver.get("https://www.instagram.com/accounts/login/?source=auth_switcher")
        sleep( waitMultiplyer * 1)
        try:
            driver.find_element_by_name("username").send_keys(username)
            driver.find_element_by_name("password").send_keys(password)
            driver.find_element_by_name("password").send_keys(Keys.ENTER)    
            sleep(waitMultiplyer * 1)
            driver.find_element_by_class_name("coreSpriteSearchIcon")
            driver.get('https://www.instagram.com/' + usernameString + '/')
            pickle.dump( driver.get_cookies() , open("/users/tayfunturanligil/Documents/getInstaCookies.pkl","wb"))

            verboseprint("Logged in")

        except Exception as e2:
            print("Failed to log in.")
            print(e2)
            print("Halting execution")
            driver.quit()
            quit()

    verboseprint("Cookies loading...")
    for cookie in cookies:
        driver.add_cookie(cookie)

def goToProfilePage(usernameString,postNo,tagged):
    '''
        Go to the instagram page of given username
        argumests: usernameString: String - the username of the profile to go
                    postNo: int - which post to get 
                    tagged: bool - is the post in profile page or in the tagged page
    '''
    if tagged:
        driver.get('https://www.instagram.com/' + usernameString + '/tagged')
    else:
        driver.get('https://www.instagram.com/' + usernameString + '/')

    sleep(waitMultiplyer *1)

    if driver.find_elements_by_css_selector(".v1Nh3 a") == []:
        print("No posts found for " + usernameString)
        print("Profile page can be private, or does not exist")
        print("Halting execution")
        driver.quit()
        quit()

    verboseprint("On profile page")

def GoToPost(postNo=1):
    try:
        sleep(waitMultiplyer *1)
        imageLinks = list(driver.find_elements_by_css_selector(".v1Nh3 a"))
        numScrolls = 0
        while (len(imageLinks) < postNo) and (numScrolls < 40):
            for i in range(3):
                print("Scrolling...")
                actions = ActionChains(driver)
                actions.send_keys(Keys.SPACE)
                actions.perform()
                actions.send_keys(Keys.SPACE)
                actions.perform()
                sleep( waitMultiplyer *1)

            for newLink in list(driver.find_elements_by_css_selector(".v1Nh3 a")):
                if newLink not in imageLinks:
                    imageLinks.append(newLink)

            numScrolls += 1

        imageLinks[postNo-1].click()
        sleep(waitMultiplyer * 0.5)
        driver.refresh()


    except Exception as e:
        print('Failed to click on post: ' + str(postNo))
        print (e)
        print("Halting execution")
        driver.quit()
        quit()


def goToPageIndex(indexToGet, usernameString):
    '''
        gets the spesified indexed page in a post
    '''
    verboseprint("Getting a single page at index: " + str(indexToGet))

    currentPageIndex = 0
    while currentPageIndex < indexToGet:
        driver.find_elements_by_class_name('coreSpriteRightChevron')[0].click()
        currentPageIndex += 1
        sleep(waitMultiplyer * 1)



def getAllPossiblePages(usernameString):
    '''
        gets all pages in a post
    '''
    morePagesExist = isThereMorePages()
    pageNo = 0
    fileNameSuffix = ''
    while True:

        if morePagesExist:
            print('Getting page ' + str(pageNo))
            fileNameSuffix = 'multi'

        img = driver.find_elements_by_tag_name('img')[min((pageNo+1),2)]
        getSinglePage(pageNo, img, usernameString, fileNameSuffix)

        if morePagesExist:
            driver.find_elements_by_class_name('coreSpriteRightChevron')[0].click()
            sleep( waitMultiplyer *.5)
            pageNo += 1
            morePagesExist = isThereMorePages()
            continue

        break

def isThereMorePages():
    """
        Check's if there are more pages in the post by checking if is there a next button
    """
    sleep(waitMultiplyer *.5)
    nextbutton = driver.find_elements_by_class_name('coreSpriteRightChevron')

    if nextbutton != []:
        print('More pages exist')
        return True   
    else:
        return False

def getSinglePage(pageNo, usernameString, fileNameSuffix=''):
    '''
        gets a single page from a potentially multi page post
        pageNo: int - which page it is getting, for printing debug info
                img: selenium object - the post we are on (asuming img at first but checking if video)
                usernameString: String - username we are on ,for printing debug info
                fileNameSuffix: String - username we are on ,for printing debug info
    '''

    try:
        video = driver.find_element_by_class_name('tWeCl') # Class tWeCl only used for videos
        print('Page '+ str(pageNo) + ' is a video')
        link_final = video.get_attribute("src")
        isVideo = True
    except:
        try:
        	img = driver.find_elements_by_tag_name('img')[min((indexToGet+1),2)]
            allLinks = img.get_attribute("srcset");
            link = allLinks.split(" ")[-2]
            link_final = link.split(",")[-1].replace("s","",1)
            isVideo = False
        except Exception as e:
            print("upsy, something bad hapened at: getSinglePost")
            print("pageNo = " + str(pageNo))
            print("img = " + str(img.text))
            print("usernameString = " + str(usernameString))
            print("fileNameSuffix = " + str(fileNameSuffix))
            print()
            print(e)
            driver.quit()

    verboseprint("Got the link for page " + str(pageNo) + "!")

    #this part works fow downloading both images and video. downloading an image can
    # be done using a one-liner, but since I need video anyway I use this for both
    try:
        path = makePathFor(usernameString, isVideo, fileNameSuffix)
        r = requests.get(link_final, stream=True)
        with open(path, 'wb') as f:
            verboseprint('Saving file')
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    f.flush()
        if openImage:
            subprocess.call(['open', path])

    except Exception as e:
        print("Failed to save file. Here is the link: ")
        print(link_final)
        print(e)
        driver.quit()
        return

def makePathFor(usernameString, isVideo, fileNameSuffix):
    '''
        Creates a path and filename for the saved file.
        all the arguments are part of the name path
    '''
    #usernameString = 'test' #for debugging

    #this path will work on any OS and added for github. 
	#In my computer I hard coded my path for simlicity
	pickleFilePath = pathlib.Path(__file__).parent / 'lastPaths.pkl'

    #I keep thack of the usernames las index in a picke and increment it for each downloaded post
    try:

        lastPaths = pickle.load(open(pickleFilePath, "rb"))
        if usernameString in lastPaths:
            no = lastPaths[usernameString]
            no += 1
            lastPaths[usernameString] = no
        else:
            no = 0
            lastPaths[usernameString] = no


    except Exception as e4:
        print("Could not open lastPaths picle, creating new one...")
        print(e4)
        lastPaths = {usernameString : 0}
        no = 0

    path = '/users/tayfunturanligil/Downloads/' + usernameString + str(no) + fileNameSuffix

    path += '.mov' if isVideo else '.jpeg'

    pickle.dump(lastPaths ,open("pickleFilePath","wb"))
    print("File name is: " + usernameString + str(no))
    return path





def main(usernamesList, postNo=[1], isHeadless=True, openImage=True, logIn=True, tagged=False, postIndex=-1):

    try:
        createDriver(isHeadless)

        if logIn:
        	logIn()

        for username in usernamesList:
            for post in postNo:

                goToProfilePage(username,post,tagged)
                GoToPost(post)

                if postIndex > -1:
                    goToPageIndex(postIndex, username)
                    getSinglePage(indexToGet, img, username)

                else:
                    getAllPossiblePages(username)

        verboseprint("Done!")

    except Exception as e:
        print("Something terrible has hapened in main")
        print(e)

    finally:
    	    driver.quit()



'''
The main script:
'''

parser = argparse.ArgumentParser()

parser.add_argument("-n", "--names", help="usernames to get", nargs='+')

parser.add_argument("-g", help="add natgeo to names", action="store_true")
parser.add_argument("-t", help="add developers_team to names", action="store_true")
parser.add_argument("-o", help="add officialfstoppers to names", action="store_true")

parser.add_argument("-d","--dont", help="dont open the posts after download", action="store_true")

parser.add_argument("--i", help="which image to get", default='1', nargs='?')
parser.add_argument("--ttikat", help="use ttikat account instead", action="store_true")
parser.add_argument("--tagged", help="get tagged pictures", action="store_true")
parser.add_argument("--index", help="index of the post", type=int, default=-1, nargs='?')

parser.add_argument("--wm", help="wait multiplier for slower connection", type=int, default=1, nargs='?')
parser.add_argument("--headly", help="Do not run in headless mode", action="store_true")
parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")

args = vars(parser.parse_args())

usernames = []
if args["g"]:
    usernames += ['natgeo']
if args["t"]:
    usernames += ['developers_team']
if args["o"]:
    usernames += ['officialfstoppers']

if args["name"]:
    usernames += args["name"].split(',')
    verboseprint("Getting for all users here: " + str(usernames))

if args["i"] is None:
    indexes = ['1']
else:
    indexes = args["i"].split(',')
    indexes = list(map(int, indexes))
    verboseprint("Getting posts at indexes: " + str(indexes))

if args["index"] is None:
    index = -1
else:
    index = args["index"]

headless = not args["headly"]
openImage = not args["dont"]
use_ttikat = args['ttikat']
tagged = args['tagged']
waitMultiplyer = args['wm']

verboseprint = print if verbose else lambda *a, **k: None

main(usernames, indexes ,headless, openImage, use_ttikat, tagged, index)







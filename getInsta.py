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


def createDriver(headless=True):
    '''
        created a global cromedriver to be used for getting posts
        arguments: headless: bool - if set to true, the chorme window will not open and operate in the backround
    '''

    global driver

    chrome_options = Options()

    if headless:
        print("Chrome is set to headless mode")
        chrome_options.add_argument("--headless")
    driver = webdriver.Chrome("/users/tayfunturanligil/Documents/chromedriver",chrome_options=chrome_options)

def logIn(ttikat=False):
    '''
        load the cookies or handle login for the defaulth account, or secondary account
        arguments: ttikat: bool - if set to true, it will log in as that account
    '''
    if ttikat:
        print("Using ttikat")
        username = 'ttikat'
    else:
        username ='tayfunforreal' 

    password = ''

    #Driver has to have done something before we can load cookies, so I ust call google
    driver.get('https://www.google.com')

    try:
        if ttikat:
            cookies = pickle.load(open("/users/tayfunturanligil/Documents/getInstaTtikatCookies.pkl", "rb"))
        else:
            cookies = pickle.load(open("/users/tayfunturanligil/Documents/getInstaCookies.pkl", "rb"))

    except Exception as e:
        print('Failed to find cookie pickle, will create a new one')
        print(e)

        driver.get("https://www.instagram.com/accounts/login/?source=auth_switcher")
        sleep( waitMultiplyer *1)
        try:
            driver.find_element_by_name("username").send_keys(username)
            driver.find_element_by_name("password").send_keys(password)
            driver.find_element_by_name("password").send_keys(Keys.ENTER)    
            sleep( waitMultiplyer *1)
            driver.find_element_by_class_name("coreSpriteSearchIcon")
            driver.get('https://www.instagram.com/' + usernameString + '/')
            pickle.dump( driver.get_cookies() , open("/users/tayfunturanligil/Documents/getInstaCookies.pkl","wb"))

            print("Logged in")

        except Exception as e2:
            print("Failed to log in.")
            print(e2)
            print("Halting execution")
            driver.quit()
            quit()

    print("Cookies loading...")
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
        numberOfPosts = getNumberOfPosts()

        #rare edge case, but if you ask for a post index higher than the num posts it will ask again
        while numberOfPosts < (postNo):
            print(usernameString + " has " + str(numberOfPosts) + " posts")
            print("You asked for post " + str(postNo))
            postNo = input("Enter post index you want: ")
            try:
                postNo = int(postNo)
            except:
                print("Not a number, halting execution")
                driver.quit()
                quit()

    sleep(waitMultiplyer *1)

    if driver.find_elements_by_css_selector(".v1Nh3 a") == []:
        print("No posts found for " + usernameString)
        print("Profile page is probably private")
        print("Halting execution")
        driver.quit()
        quit()

    print("On profile page")

def getNumberOfPosts():
    '''
        ust gets the number of posts from the profile 'headder' (instagram is probably gonna remove that info in the future)
    '''
    try:
        numPosts = float(driver.find_elements_by_class_name('g47SY')[0].text.replace(',', ''))
        return numPosts
    except Exception as e:
        print('Failed to get number of posts:')
        print(e)
        print("Halting execution")
        driver.quit()
        quit()

def clickOnPost(postNo=1):
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
        sleep(waitMultiplyer *.5)

    except Exception as e:
        print('Failed to click on post: ' + str(postNo))
        print (e)
        print("Halting execution")
        driver.quit()
        quit()

    print("Getting post " + str(postNo))

def getPageAtIndex(indexToGet, usernameString):
    '''
        gets the spesified indexed page in a post
    '''
    print("Getting a single page at index: " + str(indexToGet))
    currentPageIndex = 0
    while currentPageIndex < indexToGet:
        driver.find_elements_by_class_name('coreSpriteRightChevron')[0].click()
        currentPageIndex += 1
        sleep( waitMultiplyer *1)

    img = driver.find_elements_by_tag_name('img')[min((indexToGet+1),2)]
    getSinglePost(indexToGet, img, usernameString)


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
        getSinglePost(pageNo, img, usernameString, fileNameSuffix)

        if morePagesExist:
            driver.find_elements_by_class_name('coreSpriteRightChevron')[0].click()
            sleep( waitMultiplyer *.5)
            pageNo += 1
            morePagesExist = isThereMorePages()
            continue

        break

def isThereMorePages():
    """
        Check's if there are more pages in the post bu checking if is there a next button
    """
    sleep(waitMultiplyer *.5)
    nextbutton = driver.find_elements_by_class_name('coreSpriteRightChevron')

    if nextbutton != []:
        print('More pages detected!')
        return True   
    else:
        return False

def getSinglePost(pageNo, img, usernameString, fileNameSuffix=''):
    '''
        gets a single post from a potentially multi page post
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

    print("Got the link for page " + str(pageNo) + "!")

    #this part works fow downloading both images and video. downloading an image can
    # be done using a one liner, but since I need video anyway I use this for both
    try:
        path = makePathFor(usernameString, isVideo, fileNameSuffix)
        r = requests.get(link_final, stream=True)
        with open(path, 'wb') as f:
            print('Saving file')
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    f.flush()
        if openImage:
            subprocess.call(['open', path])

    except Exception as e3:
        print("Failed to save file. Here is the link: ")
        print(link_final)
        print(e3)
        driver.quit()
        return

def makePathFor(usernameString, isVideo, fileNameSuffix):
    '''
        Creates a path and filename for the saved file.
        all the arguments are part of the name path
    '''
    usernameString = usernameString[:3]
    #usernameString = 'test'
    if isVideo:
        usernameString += 'V'

    #I keep thack of the usernames las index in a picke and increment it for each downloaded post
    try:
        lastPaths = pickle.load(open("/users/tayfunturanligil/Documents/lastPaths.pkl", "rb"))
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

    pickle.dump(lastPaths ,open("/users/tayfunturanligil/Documents/lastPaths.pkl","wb"))
    print("File name is: " + usernameString + str(no))
    return path




def main(usernamesList, postNo=[1], headless=True, openImage=True, use_ttikat=False, tagged=False, postIndex=-1):

    try:
        createDriver(headless)
        logIn(use_ttikat)
        for username in usernamesList:
            for post in postNo:
                post = int(post)
                goToProfilePage(username,post,tagged)
                clickOnPost(post)
                driver.refresh()
                if postIndex > -1:
                    getPageAtIndex(postIndex, username)
                else:
                    getAllPossiblePages(username)

        driver.quit()
        print("Done!")

    except Exception as e:
        print("Something terrible has hapened in main")
        print(e)
        driver.quit()




parser = argparse.ArgumentParser()

parser.add_argument("-n", "--name", help="usernames to get. If have multiple, seperate with ',' and no spaces")
parser.add_argument("-m", action="store_true")
parser.add_argument("-a", action="store_true")
parser.add_argument("-l", action="store_true")
parser.add_argument("-r", action="store_true")
parser.add_argument("-c", action="store_true")
parser.add_argument("-o", action="store_true")
parser.add_argument("-e", action="store_true")

parser.add_argument("-d","--dont", help="dont open the image", action="store_true")

parser.add_argument("--i", help="which image to get", default='1', nargs='?')
parser.add_argument("--wm", help="wait multiplier for slower connection", type=int, default=1, nargs='?')

parser.add_argument("--headly", help="Do not run in headless mode", action="store_true")
parser.add_argument("--ttikat", help="use ttikat account instead", action="store_true")
parser.add_argument("--tagged", help="get tagged pictures", action="store_true")
parser.add_argument("--index", help="index of the post", type=int, default=-1, nargs='?')

args = vars(parser.parse_args())

usernames = []

if args["a"]:
    usernames += ['']
if args["m"]:
    usernames += ['']
if args["l"]:
    usernames += ['']
if args["r"]:
    usernames += ['']
if args["c"]:
    usernames += ['']
if args["o"]:
    usernames += ['']
if args["e"]:
    usernames += ['']
    args['ttikat'] = True

if args["name"]:
    usernames += args["name"].split(',')
    print("Getting for all users here: " + str(usernames))

if args["i"] is None:
    indexes = ['1']
else:
    indexes = args["i"].split(',')
    print("Getting posts at indexes: " + str(indexes))

if args["index"] is None:
    index = -1
else:
    index = args["index"]

headless = not args["headly"]
openImage = not args["dont"]
use_ttikat = args['ttikat']
tagged = args['tagged']
waitMultiplyer = args['wm']

main(usernames, indexes ,headless, openImage, use_ttikat, tagged, index)







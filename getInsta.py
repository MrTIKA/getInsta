#!/Library/Frameworks/Python.framework/Versions/3.7/bin/python3

import pickle
import os
import argparse
import requests
import subprocess
import pathlib
from functools import partial
from time import sleep

import selenium.webdriver as webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options

#TODO:
#Make configration file for pickle locations

def createDriver(headless):
	'''
		created a global cromedriver to be used for getting posts
		arguments: headless: bool - if set to true, the chorme window will not open and operate in the backround
	'''

	global driver
	chrome_options = Options()

	if headless:
		verboseprint("Chrome is set to headless mode")
		chrome_options.add_argument("--headless")
	driver = webdriver.Chrome(executable_path= os.path.expanduser("~/Documents/chromedriver"), options=chrome_options)

def logIn():
	'''
		load the cookies or handle login for the defaulth account, or secondary account
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
			driver.get('https://www.instagram.com/' + username + '/')
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

def goToProfilePage(username,tagged):
	'''
		Go to the instagram page of given username
		argumests: username: String - the username of the profile to go
					postNo: int - which post to get 
					tagged: bool - is the post in profile page or in the tagged page
	'''
	if tagged:
		driver.get('https://www.instagram.com/' + username + '/tagged')
	else:
		driver.get('https://www.instagram.com/' + username + '/')

	sleep(waitMultiplyer *1)

	if driver.find_elements_by_css_selector(".v1Nh3 a") == []:
		print("No posts found for " + username)
		print("Profile page can be private, or does not exist")
		print("Halting execution")
		driver.quit()
		quit()

	verboseprint("On profile page")

def goToPost(postNo):
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


def goToPageIndex(pageIndex):
	'''
		gets the spesified indexed page in a post
	'''
	verboseprint("Getting a single page at index: " + str(pageIndex))

	currentPageIndex = 0
	while currentPageIndex < pageIndex:
		#the next page button
		driver.find_elements_by_class_name('coreSpriteRightChevron')[0].click()
		currentPageIndex += 1
		sleep(waitMultiplyer * 1)


def getAllPossiblePages():
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
		getSinglePage(pageNo, fileNameSuffix)

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
		verboseprint('More pages exist')
		return True   
	else:
		return False

def getSinglePage(pageIndex, fileNameSuffix=''):
	'''
		gets a single page from a potentially multi page post
		pageIndex: int - need to find the image link becaus insta caches multiple image links in a list
				img: selenium object - the post we are on (asuming img at first but checking if video)
				fileNameSuffix: String - I like to spesify multi page posts
	'''

	try:
		video = driver.find_element_by_class_name('tWeCl') # Class tWeCl only used for videos
		verboseprint('Page '+ str(pageIndex) + ' is a video')
		link_final = video.get_attribute("src")
		isVideo = True

	except:
		try:
			img = driver.find_elements_by_tag_name('img')[min((pageIndex+1),2)]
			allLinks = img.get_attribute("srcset");
			link = allLinks.split(" ")[-2]
			link_final = link.split(",")[-1].replace("s","",1)
			isVideo = False
		except Exception as e:
			print("upsy, something bad hapened at getSinglePost: ")
			print(e)
			print("pageIndex = " + str(pageIndex))
			print("img = " + str(img.text))
			print("fileNameSuffix = " + str(fileNameSuffix))
			print()
			driver.quit()

	verboseprint("Got the link for page " + str(pageIndex) + "!")

	#this part works fow downloading both images and video. downloading an image can
	# be done using a one-liner, but since I need video anyway I use this for both
	try:
		pathToSave = partialMakePathFor(isVideo, fileNameSuffix)
		r = requests.get(link_final, stream=True)
		with open(pathToSave, 'wb') as f:
			verboseprint('Saving file')
			for chunk in r.iter_content(chunk_size=1024):
				if chunk:
					f.write(chunk)
					f.flush()
		if openImage:
			subprocess.call(['open', pathToSave])

	except Exception as e:
		print("Failed to save file in getSinglePage(). Here is the link: ")
		print(link_final)
		print("Eroor is: ")
		print(e)
		print("pathToSave is:")
		print(pathToSave)

		driver.quit()
		return

def makePathFor(username, isVideo, fileNameSuffix):
	'''
		Creates a path and filename for the saved file.
		all the arguments are part of the name path
	'''
	#username = 'test' #for debugging

	#this path will work on any OS and added for github. 
	#In my computer I hard coded my path for simlicity

	pickleFilePath = pathlib.Path(__file__).parent / 'lastPaths.pkl'

	#I keep thack of the usernames las index in a picke and increment it for each downloaded post
	try:

		lastPaths = pickle.load(open(pickleFilePath, "rb"))
		if username in lastPaths:
			no = lastPaths[username]
			no += 1
			lastPaths[username] = no
		else:
			no = 0
			lastPaths[username] = no


	except Exception as e4:
		print("Could not open lastPaths picle, creating new one...")
		print(e4)
		lastPaths = {username : 0}
		no = 0

	path = os.path.expanduser("~/Downloads/") + username + str(no) + fileNameSuffix

	path += '.mov' if isVideo else '.jpeg'

	pickle.dump(lastPaths ,open(pickleFilePath,"wb"))
	print("File name is: " + username + str(no))

	return path




def main(
		usernamesList=[], 
		postIndexes=[1], 
		isHeadless=True, 
		openImage=True, 
		needLogIn=True, 
		tagged=False, 
		pageIndex=-1):

	try:
		createDriver(isHeadless)

		if needLogIn:
			logIn()

		for username in usernamesList:
			for postIndex in postIndexes:

				goToProfilePage(username,tagged)
				goToPost(postIndex)

				partialMakePathFor = partial(makePathFor(username))
				if pageIndex > -1:
					goToPageIndex(pageIndex)
					getSinglePage(pageIndex)
				else:
					getAllPossiblePages()

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

parser.add_argument("--i", help="which images to get, first image is 1. list numbers with comas in between", default='1', nargs='?')
parser.add_argument("--guest", help="do not rqure log in", action="store_true")
parser.add_argument("--tagged", help="get tagged pictures", action="store_true")
parser.add_argument("--page", help="index of the page, 0 is first page, defauth is get all pages of post", type=int, default=-1, nargs='?')

parser.add_argument("--wm", help="wait multiplier for slower connection", type=int, default=1, nargs='?')
parser.add_argument("--headly", help="Do not run in headless mode", action="store_true")
parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")

args = vars(parser.parse_args())

verboseprint = print if args["verbose"] else lambda *a, **k: None

usernames = []
if args["g"]:
	usernames += ['natgeo']
if args["t"]:
	usernames += ['developers_team']
if args["o"]:
	usernames += ['officialfstoppers']

if args["names"]:
	usernames += args["names"]#.split(',')
	verboseprint("Getting for all users here: " + str(usernames))

if args["i"] is None:
	postIndexes = ['1']
else:
	postIndexes = args["i"].split(',')
	postIndexes = list(map(int, postIndexes))
	verboseprint("Getting posts at indexes: " + str(postIndexes))

if args["page"] is None:
	pageIndex = -1
else:
	pageIndex = args["page"]


headless = not args["headly"]
openImage = not args["dont"]
guest = args['guest']
tagged = args['tagged']
waitMultiplyer = args['wm']


main(usernames, postIndexes ,headless, openImage, guest, tagged, pageIndex)







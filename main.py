import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
import smtplib
import sys
import credentials
import json
import requests

## check if logged in
def isLoggin(driver):
    driver.get("https://disneyplus.com")
    isLogged = False
    try:
        loginButton = driver.find_element_by_xpath("""//*[@id="nav-bar"]/div/div/button[1]""")
        isLogged = False
    except:
        isLogged = True

    return isLogged

## Login 
def login(driver):
    print (" Sign In ")
    driver.get("https://disneyplus.com/login")

    ## --------------- Type Email Address -------------------
    # waits for email input box
    while True:
        try:
            emailInput = driver.find_element_by_name("email")
            if emailInput:
                break
            continue
        except:
            continue
    
    # set email address to email field
    email = driver.find_element_by_name("email")
    email.clear()
    email.send_keys(credentials.email)

    # click the submit button
    driver.find_element_by_name("dssLoginSubmit").click()
    
    ## --------------- Type Password -------------------
    # wait for password input box
    while True:
        try:
            passwordInput = driver.find_element_by_name("password")
            if passwordInput:
                break
            continue
        except:
            continue
    # set password to password field
    password = driver.find_element_by_name("password")
    password.clear()
    password.send_keys(credentials.password)

    # click the submit button
    driver.find_element_by_name("dssLoginSubmit").click()

## Click action for next arrow button
def clickNextInSection(driver, element):
    driver.execute_script("arguments[0].scrollIntoView();", element)
    while True:
        try:
            # [1] is next arrow button, [0] is prev arrow button  
            element.find_elements_by_tag_name("button")[1].click()
            sleep(0.5)
            continue
        except:
            break

## Scan whole pages to get sections and movies (just Name and Image)    
def pageScan(driver):
    # Page Information Object
    pageInformation = None

    # Read the data that was saved
    try:
        with open('temp.json') as f:
            pageInformation = json.load(f)
    except:
        pass

    # waits for the @id[home-collection] div
    while True:
        try:
            homeCollection = driver.find_element_by_id("home-collection")
            break
        except:
            continue
    sleep(5)

    # if previous Page Information is valid, then skip to scan page.
    if pageInformation != None:
        return pageInformation

    print (" Page Scanning ... ")
    divs = driver.find_elements_by_xpath("""//*[@id="home-collection"]/div/div""")
    lengthOfSections = len(divs) - 2
    lengthOfActives = len(divs[2].find_elements_by_class_name("slick-active"))
    i = 0

    sections = [] ## sections data

    # div[0] => Slider 
    # div[1] => Brands    
    for div in divs:
        i = i + 1
        if i < 3:
            continue
        
        # click next arrow to show all videos
        clickNextInSection(driver, div)

        # get Section Name and Images
        h4 = div.find_element_by_xpath(""".//h4""")
        sectionName = h4.get_attribute("innerHTML")

        imgs = div.find_elements_by_xpath(""".//img""")
        items = []
        for img in imgs:
            items.append({
                "Name": img.get_attribute('alt'),
                "Image": img.get_attribute('src'),
                "URL": ""
            })
        
        sections.append({
            "Name": sectionName,
            "Items": items
        })

    print (" Page Scanning ... Done")
    return {
        "sectionsLen": lengthOfSections,
        "activeLen": lengthOfActives,
        "sectionList": sections,
        "sectionIndex": 0,
        "itemIndex": 0
    }

## move to section, forexample - show the "Recommend For You" section to the clientview
def moveToSection(driver, element):
    driver.execute_script("arguments[0].scrollIntoView();", element)

## move to item (selected)
#  itemIndex - 0, 1, 2, ...
#  activeLen - 4 (count that is showed actively in specific section)
def moveToItem(driver, element, itemIndex, activeLen):
    page = int(itemIndex / activeLen)
    
    while page > 0:
        print ("Page", page)
        try:
            page = page - 1
            element.find_elements_by_tag_name("button")[1].click()
            sleep(0.5)
        except:
            sleep(0.5)
            print ("Error1234")
            continue

##  Scrape Data - Get URL 
def scrapeItem(driver, element, itemIndex):
    aTags = element.find_elements_by_xpath(""".//a""")
    aTag = aTags[itemIndex]
    actions = ActionChains(driver)
    try:
        actions.move_to_element_with_offset(aTag, 140, 90).perform()
        aTag.click()
    except Exception as e:
        print (e)
        ## Close React Modal Overlay for the scrapping error.
        button = driver.find_element_by_xpath("""//div[@class=ReactModal__Overlay]""")
        button.click()
        aTag.click()

    sleep(1)
    movieLink = driver.current_url
    sleep(0.5)
    driver.back()
    return movieLink

## Scan Item
# sectionIndex - 0, 1, 2, ...
# itemIndex - 0, 1, 2, ...
# activeLen - length of active items (default 4)
# sections - json object to store
def itemScan(driver, sectionIndex, itemIndex, activeLen, sections):
    section = None
    sleep(2)
    isSessionInvalid = False
    while True:
        try:
            divs = driver.find_elements_by_xpath("""//*[@id="home-collection"]/div/div""")
            section = divs[sectionIndex + 2]
            break
        except:
            continue
    if isSessionInvalid:
        ## if session error, data should be saved.
        with open('data.json', 'w') as f:
            json.dump(sections, f, indent=4, sort_keys=False)

    URL = ''

    try:
        ## get section name
        h4 = section.find_element_by_xpath(""".//h4""")
        sectionName = h4.get_attribute("innerHTML")
        ## move to selected section
        moveToSection(driver, section)
        
        ## move to selected Item
        moveToItem(driver, section, itemIndex, activeLen)

        ## scrape data for the selected item
        URL = scrapeItem(driver, section, itemIndex)

    except Exception as e:
        print (e)
    return URL
    
    

def main():
    PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
    DRIVER_BIN = os.path.join(PROJECT_ROOT, "bin/chromedriver")
    
    driver = webdriver.Chrome(executable_path = DRIVER_BIN)
    isLogged = isLoggin(driver)
    
    if isLogged == False:
        login(driver)
    
    pageInformations = pageScan(driver)

    sectionsLen = pageInformations['sectionsLen']
    activeLen = pageInformations['activeLen']
    sections = pageInformations['sectionList']
    sectionIndex = pageInformations['sectionIndex']
    itemIndex = pageInformations['itemIndex']

    ## click prev button for the first section
    divs = driver.find_elements_by_xpath("""//*[@id="home-collection"]/div/div""")
    section = divs[sectionIndex + 2]
    moveToSection(driver, section)
    while True:
        try:  
            section.find_elements_by_tag_name("button")[0].click()
            sleep(0.5)
            continue
        except:
            break
            
    ## start the scraping
    print ("Section ---------- ", sectionIndex, "----------")
    while True:
        try:
            print ("Item ... ", itemIndex)
            URL = itemScan(driver, sectionIndex, itemIndex, activeLen)
            itemIndex = itemIndex + 1
            sections[sectionIndex]['Items'][itemIndex - 1]['URL'] = URL
            print (json.dumps(sections[sectionIndex]['Items'][itemIndex - 1], indent=4))
            
            if itemIndex >= len(sections[sectionIndex]['Items']):
                sectionIndex = sectionIndex + 1
                itemIndex = 0
                if sectionIndex >= sectionsLen:
                    break
                print ("Section ---------- ", sectionIndex, "----------")

            pageInformations['sectionIndex'] = sectionIndex
            pageInformations['itemIndex'] = itemIndex
            with open('temp.json', 'w') as f:
                json.dump(pageInformations, f, indent=4, sort_keys=False)
        except Exception as e:
            continue
        
    with open('data.json', 'w') as f:
        json.dump(sections, f, indent=4, sort_keys=False)
    sleep(5000)
    
if __name__ == '__main__':
    main()
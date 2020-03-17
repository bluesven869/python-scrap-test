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

def isLoggin(driver):
    driver.get("https://disneyplus.com")
    isLogged = False
    try:
        loginButton = driver.find_element_by_xpath("""//*[@id="nav-bar"]/div/div/button[1]""")
        isLogged = False
    except:
        isLogged = True

    return isLogged

def login(driver):
    print (" Sign In ")
    driver.get("https://disneyplus.com/login")
    while True:
        try:
            emailInput = driver.find_element_by_name("email")
            if emailInput:
                break
            continue
        except:
            continue
    
    email = driver.find_element_by_name("email")
    email.clear()
    email.send_keys(credentials.email)
    driver.find_element_by_name("dssLoginSubmit").click()
    
    while True:
        try:
            passwordInput = driver.find_element_by_name("password")
            if passwordInput:
                break
            continue
        except:
            continue
    password = driver.find_element_by_name("password")
    password.clear()
    password.send_keys(credentials.password)
    driver.find_element_by_name("dssLoginSubmit").click()

def clickNextInSection(driver, element):
    driver.execute_script("arguments[0].scrollIntoView();", element)
    while True:
        try:  
            element.find_elements_by_tag_name("button")[1].click()
            sleep(0.5)
            continue
        except:
            break
    
def pageScan(driver):
    pageInformation = None
    try:
        with open('temp.json') as f:
            pageInformation = json.load(f)
    except:
        pass

    while True:
        try:
            homeCollection = driver.find_element_by_id("home-collection")
            break
        except:
            continue
    sleep(5)

    if pageInformation != None:
        return pageInformation

    print (" Page Scanning ... ")
    divs = driver.find_elements_by_xpath("""//*[@id="home-collection"]/div/div""")
    lengthOfSections = len(divs) - 2
    lengthOfActives = len(divs[2].find_elements_by_class_name("slick-active"))
    i = 0
    sections = []
    for div in divs:
        i = i + 1
        if i < 3:
            continue
        
        clickNextInSection(driver, div)
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

def moveToSection(driver, element):
    driver.execute_script("arguments[0].scrollIntoView();", element)

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

def scrapeItem(driver, element, itemIndex):
    aTags = element.find_elements_by_xpath(""".//a""")
    aTag = aTags[itemIndex]
    actions = ActionChains(driver)
    try:
        actions.move_to_element_with_offset(aTag, 140, 90).perform()
        aTag.click()
    except Exception as e:
        print("_DD_D_D_")
        print (e)

        button = driver.find_element_by_xpath("""//div[@class=ReactModal__Overlay]""")
        button.click()
        aTag.click()

    sleep(1)
    movieLink = driver.current_url
    sleep(0.5)
    driver.back()
    return movieLink


def itemScan(driver, sectionIndex, itemIndex, activeLen):
    section = None
    sleep(2)
    while True:
        try:
            divs = driver.find_elements_by_xpath("""//*[@id="home-collection"]/div/div""")
            section = divs[sectionIndex + 2]
            break
        except Exception as e:
            print("AAAA")
            print(e)
            continue
    
    URL = ''
    try:
        h4 = section.find_element_by_xpath(""".//h4""")
        sectionName = h4.get_attribute("innerHTML")
        moveToSection(driver, section)
        print("MOVE TO SECTION DONE")
        moveToItem(driver, section, itemIndex, activeLen)
        print("MOVE TO ITEM DONE")
        URL = scrapeItem(driver, section, itemIndex)
        print ("URL", URL)
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
    sectionIndex = 4
    itemIndex = 21

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
            
            print ("SectionsLen", sectionsLen, ", Section: ", sectionIndex, ", Item:", itemIndex, ", Length of Items:", len(sections[sectionIndex]['Items']) )
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
            print('ERROR :::: ')
            print(e)
            continue
        
    with open('data.json', 'w') as f:
        json.dump(sections, f, indent=4, sort_keys=False)        
    sleep(5000)
    
if __name__ == '__main__':
    main()
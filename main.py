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
    sleep(0.5)
    driver.execute_script("arguments[0].scrollIntoView();", element)
    while True:
        try:
            element.find_elements_by_tag_name("button")[1].click()
            sleep(1)
            continue
        except Exception as e:
            break
    

def pageScan(driver):
    while True:
        try:
            homeCollection = driver.find_element_by_id("home-collection")
            break
        except:
            continue
    ## waits 5 seconds
    sleep(5)
    divs = driver.find_elements_by_xpath("""//*[@id="home-collection"]/div/div""")
    action = ActionChains(driver)
    sections = []
    for div in divs:
        try:
            h4 = div.find_element_by_xpath(""".//h4""")
            sectionName = h4.get_attribute("innerHTML")
            print("Scanning...", sectionName)
            clickNextInSection(driver, div)
            items = []
            imgs = div.find_elements_by_xpath(""".//img""")
            for img in imgs:
                movieName = img.get_attribute("alt")
                movieImage = img.get_attribute("src")
                items.append({
                    "Name": movieName,
                    "Image": movieImage
                })
            
            

            # aTags[0].click()
            # for aTag in aTags:
            #     print(aTag.get_attribute('onClick'))
            
            sections.append({
                "Name": sectionName,
                "Items": items
            })

        except Exception as e:
            print (e)
            continue
    
    with open('data.json', 'w') as f:
        json.dump(sections, f, indent=4, sort_keys=False)

def main():
    PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
    DRIVER_BIN = os.path.join(PROJECT_ROOT, "bin/chromedriver")
    
    driver = webdriver.Chrome(executable_path = DRIVER_BIN)
    isLogged = isLoggin(driver)
    
    if isLogged == False:
        login(driver)
    contentData = getContentsFromGraphQL(driver)
    for container in contentData.CollectionBySlug.containers:
        if container.type != "ShelfContainer":
            continue
        container.items
    pageScan(driver)
    sleep(5000)
    
if __name__ == '__main__':
    main()
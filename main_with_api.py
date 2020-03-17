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

def verifyDevice():
    url = "https://global.edge.bamgrid.com/devices"
    payload = "{\n\t\"deviceFamily\": \"browser\",\n\t\"applicationRuntime\": \"chrome\",\n\t\"deviceProfile\": \"linux\",\n\t\"attributes\": {}\n}"
    headers = {
        'content-type': 'application/json; charset=UTF-8',
        'x-bamsdk-client-id': 'disney-svod-3d9324fc',
        'x-bamsdk-platform': 'linux',
        'x-bamsdk-version': '4.4',
        'Authorization': 'Bearer ZGlzbmV5JmJyb3dzZXImMS4wLjA.Cu56AgSfBTDag5NiRA81oLHkDZfu5L3CKadnefEAY84'
    }
    response = requests.request("POST", url, headers=headers, data = payload)
    return json.loads(response.text.encode('utf8'))

def getToken(deviceToken):
    url = "https://global.edge.bamgrid.com/token"
    payload = {
        'grant_type': 'urn:ietf:params:oauth:grant-type:token-exchange',
        'subject_token': deviceToken,
        'subject_token_type': 'urn:bamtech:params:oauth:token-type:device',
        'platform': 'browser',
        'latitude': '0',
        'longitude': '0'
    }
    files = [ ]
    headers = {
        'content-type': 'application/x-www-form-urlencoded',
        'x-bamsdk-client-id': 'disney-svod-3d9324fc',
        'x-bamsdk-platform': 'linux',
        'x-bamsdk-version': '4.4',
        'accept-language': 'en-US,en;q=0.9',
        'Authorization': 'Bearer ZGlzbmV5JmJyb3dzZXImMS4wLjA.Cu56AgSfBTDag5NiRA81oLHkDZfu5L3CKadnefEAY84'
    }
    response = requests.request("POST", url, headers=headers, data = payload, files = files)
    return json.loads(response.text.encode('utf8'))

def getData(token):
    url = "https://search-api-disney.svcs.dssott.com/svc/search/v2/graphql/persisted/query/core/CollectionBySlug?variables=%7B%22preferredLanguage%22%3A%5B%22en%22%5D%2C%22contentClass%22%3A%22home%22%2C%22slug%22%3A%22home%22%2C%22contentTransactionId%22%3A%22935ea430-80f9-4b29-90fd-e2f1dc77d76f%22%7D"
    payload = {}
    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
    }
    response = requests.request("GET", url, headers=headers, data = payload)
    return json.loads(response.text.encode('utf8'))

def main():
    sections = []
    contentData = verifyDevice()
    token = getToken(contentData['assertion'])
    data = getData(token['access_token'])
    containers = data['data']['CollectionBySlug']['containers']
    for container in containers:
        if container['type'] == 'ShelfContainer':
            containerSet = container['set']
            containerName = containerSet['texts'][0]['content']
            itemsJson = None
            try:
                itemsJson = containerSet['items']
            except Exception as e:
                print (containerName, 'skipped')
                print (e)
                continue

            print(containerName, " ...")
            items = []
            for item in containerSet['items']:
                try:
                    encodedFamilyId = item['families'][0]['encodedFamilyId']
                    movieSlug = ''
                    movieType = ''
                    if item['type'] == 'DmcVideo':
                        movieType = 'movies'
                    for txtObj in item['texts']:
                        if txtObj['type'] == 'slug':
                            movieSlug = txtObj['content']
                        if txtObj['type'] == 'full' and txtObj['field'] == 'title':
                            movieName = txtObj['content']
                    actionLink = 'https://disneyplus.com/' + movieType + '/' + movieSlug + '/' + encodedFamilyId
                    imageUrl = ''
                    for imgObj in item['images']:
                        if imgObj['purpose'] == 'hero_tile':
                            imageUrl = imgObj['url'] + '/scale?width=800&aspectRatio=1.78&format=jpeg'
                            break

                    items.append({"Name": movieName, "Image": imageUrl, "URL": actionLink})
                except Exception as e:
                    print (e)
                    continue
            
            sections.append({
                "Name": containerName,
                "Items": items
            })
    # print(json.dumps(sections, indent=4))
    # print (len(sections))
    sleep(5000)
    
if __name__ == '__main__':
    main()
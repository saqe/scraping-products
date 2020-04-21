import requests as re
from bs4 import BeautifulSoup
import json
from requests.exceptions import ConnectionError
from util.AntiRecaptcha import AntiRecaptcha
from util.ReadCSVList import ReadCSVList
from util.FileFlagHandler import FileFlagHandler
from util.StoreLogs import StoreCSVLogs
from _discord_.DiscordNotification import DiscordNotification
import time
from datetime import datetime
from DataHandling.MongoHandler import MongoHandler
from dotenv import load_dotenv
import os
import logging
from simplejson.scanner import JSONDecodeError as JSONDecodeError
import traceback
logging.basicConfig(filename='scraping.log', filemode='a', format='%(asctime)s %(levelname)-8s %(message)s',level=logging.INFO)
logger = logging.getLogger()

#Load ENVIRONMENT VARIABLES
load_dotenv()

re=re.Session()

db=MongoHandler(os.getenv('MONGO_DB_API'))

read_file=ReadCSVList("Categories.csv")
CATEGORIES=read_file.readColoumnFromFile(skipHeader=True)
CATEGORIES=read_file.getFileToList()[::-1]

notification=DiscordNotification(os.getenv('DISCORD_HOOK_PROGRESS_UPDATE'))
recaptacha_notification=DiscordNotification(os.getenv('DISCORD_HOOK_RECAPTACHA'))

recaptacha_solver=AntiRecaptcha(os.getenv('ANTI_RECAPTACHA_CLIENT'),os.getenv('RECAPTACHA_SITE_ID'),os.getenv('RECAPTACHA_SITE_LINK'))

recaptacha_solver.set_discord_channel(os.getenv('DISCORD_HOOK_RECAPTACHA'))

logs_db=StoreCSVLogs('LOGS_CATEGORIES.csv')
logs_db.loadLogs()

excute_flag=FileFlagHandler('DISCORD_FILE_FLAG')
MAIN_URL='https://www.idealo.de'

requestHeader={
  'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
  'accept-language': 'en-US,en;q=0.9',
  'accept-encoding': 'gzip, deflate, br',
  'cache-control': 'no-cache',
  'pragma': 'no-cache',
  'upgrade-insecure-requests': '1',
  'cookie':os.getenv('COOKIES'),
  'user-agent': os.getenv('USER_AGENT_CHROME')
}


first_time=True
post_request=requestHeader
post_request['content-type']='application/x-www-form-urlencoded'

def is_it_solved(response):
  start=time.time()
  logger.info("Waiting for POST response from www.idealo.de")
  reponse=re.post('https://www.idealo.de',data={'g-recaptcha-response':response},headers=post_request)
  time_taken="\nTime taken : "+str((time.time()-start))
  logger.info("Response :"+str(reponse.status_code))
  if reponse.status_code!=200:
    logger.info("Error with recaptacha")
    recaptacha_notification.sendErrorMessage("Response : "+str(reponse.status_code)+"\nSome Problem"+time_taken,"Failed")
    recaptacha_solver.incorrect()

def scrape_product_page(dataDict):
  global first_time
  url=dataDict['Product Link']
  while True:
    try:
      page=re.get(url,headers=requestHeader)
    except ConnectionError:
      notification.sendWarningMessage("Error with "+(url)+"\nTrying Again.")
      time.sleep(30)
      continue

    if page.status_code!=200: print('[!] Page status code: ',page.status_code)

    pageParser=BeautifulSoup(page.content,'html.parser')
    if pageParser.find('body',id='captcha') is not None:
      print("Captcha being solved")
      recaptacha_notification.sendInfoMessage("Recaptacha Shown up, waiting to be solved\nProducts : "+str(db.count_records()),"Recaptcha Found")
      start=time.time()
      response=recaptacha_solver.getResponse()
      time_taken="\nTime taken : "+str((time.time()-start))
      recaptacha_notification.sendSuccessMessage("Recaptacha Solved by vendor"+time_taken)
      is_it_solved(response)
      continue
    break

  print(dataDict['Product Title'])
  for row in pageParser.find('div',id="Datenblatt").find('ul',class_='datasheet-list').findAll('li',class_='datasheet-listItem--properties'):
    key=row.find('span',class_='datasheet-listItemKey').getText().strip()
    value=row.find('span',class_='datasheet-listItemValue').getText().strip()

    # MongoDB don't accept . $ and \i in key values
    dataDict[db.encode_key(key)]=value
  db.store_product(dataDict)

def main():
  for CATEGORY_LINK in CATEGORIES:
    CATEGORY_ID=str(int(CATEGORY_LINK.split('/')[-1].split('.')[0]))
    if logs_db.ifDataInLogs(CATEGORY_ID):continue
    notification.sendInfoMessage("Started category code: "+CATEGORY_ID+"\n"+CATEGORY_LINK)
    # print("Category: "+CATEGORY_ID)
    CATEGORY_JSON_API=os.getenv('CATEGORY_JSON_LINK').format(category_id=CATEGORY_ID)
    try:
      while True:
        json_page=re.get(CATEGORY_JSON_API)
        logger.info("Link "+str(CATEGORY_JSON_API)+"\n Status code is :"+str(json_page.status_code))
        if json_page.status_code!=200:
          logger.error("Error with category id:"+CATEGORY_ID)
          logger.error("Category link:"+CATEGORY_LINK+" might having some problem with")

          notification.sendErrorMessage("ERROR with category: "+CATEGORY_ID+"\nResoponse code : "+str(json_page.status_code),'Invalid Response Code')
        
        #Hande JSON Exception here
        JSON_RESULT=json_page.json()
        for product in JSON_RESULT['categoryJsonResults']["entries"]:
          dataDict={}
          try:
            if 'id' in product['link']['productLink']: dataDict['_id']=product['link']['productLink']['id']
            else: dataDict['_id']=product['link']['productLink']['Id']
            category_name=product['categoryName']
          except TypeError as te:
            # notification.sendErrorMessage("TypeError with product id of : "+CATEGORY_JSON_API,"Error")
            logger.exception("Id is replaced with ebay or something like that")
            continue
          # if Product is already scraped   
          if db.if_product_exists(dataDict['_id']):continue
          
          product_link=product['link']['productLink']['href']
          if not product_link.startswith('http'):
            product_link=MAIN_URL+product_link
          dataDict['Product Link']=product_link
          dataDict['Product Type']=product['type']
          dataDict['Product Title']=product['title'].strip()
          dataDict['Category']=product['categoryName']
          
          scrape_product_page(dataDict)

        pagination=JSON_RESULT["categoryPagination"]
        if pagination is None:
          notification.sendErrorMessage("Pagination is None,\nCategory API Link:"+str(CATEGORY_JSON_API)+"\n Category Link "+str(CATEGORY_LINK),"Pagination")  
          break
        if pagination['nextPageAjaxLink'] is None:break
        CATEGORY_JSON_API=pagination['nextPageAjaxLink']
    except JSONDecodeError:
      notification.sendErrorMessage("(Category ID change) Error with JSON category "+CATEGORY_LINK+" moving to next.","JSON Decode Error")
      logs_db.store_data(CATEGORY_ID)
      continue
    
    logs_db.store_data(CATEGORY_ID)
    try:
      notification.sendSuccessMessage("Category : "+str(category_name)+" #"+str(CATEGORY_ID)+" is completed\n"+str(db.getCategoryValueCount(category_name)))
    except UnboundLocalError:
      notification.sendSuccessMessage("Current category is completed")
    

if __name__ == "__main__":
    try:main()
    except Exception as p:
      notification.sendErrorMessage(str(traceback.format_exc()),type(p).__name__)


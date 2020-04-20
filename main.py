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
  'cookie':'SSID=CAAS9h2MAAAAAAB6MpZefXREAHoyll4BAAAAAAAAAAAAejKWXgIfvNYCAAHYSQAAejKWXgEA_gIAARBOAAB6MpZeAQAEAwADSE4AAHoyll4BACIDAAPCUwAAejKWXgEAHQMAA5RSAAB6MpZeAQDmAgABcEsAAHoyll4BAN4CAAEpSwAAejKWXgEAGAMAAcFQAAB6MpZeAQDzAgADvEwAAHoyll4BAB8DAAGkUgAAejKWXgEA; SSSC=1.G6815690585643709565.1|726.18904:734.19241:742.19312:755.19644:764.19943:766.19984:772.20040:792.20673:797.21140:799.21156:802.21442; SSRT=jzKWXgADAA; SSPV=LEYAAAAAAA4ADgAAAAAAAAAAAAMAAAAAAAAAAAAA; SSLB=1; JSESSIONID=4391FE56E47517DE6943CDCC9B9EDBFD; ipcuid=010vm2ci00k90g97xc; icda=1; _gaaw_ga=GA1.1.104273216.1586901626; _gaaw_ga_3QKDZ6V5EG=GS1.1.1586901625.1.1.1586901652.0; _dcmn_p=7U-4Y2lkPU56cDByRjZXTW51ZEcyTmVBSms; _dcmn_p=7U-4Y2lkPU56cDByRjZXTW51ZEcyTmVBSms; _dcmn_p=7U-4Y2lkPU56cDByRjZXTW51ZEcyTmVBSms; SSOD=AJEBAAAAEAAARAAABAAAAI8yll6XMpZeAAA; _gcl_au=1.1.645103697.1586901647; _uetsid=_uet09905b85-0b75-cf0e-21b5-9707d5a247df',
  'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',
}


first_time=True
post_request=requestHeader
post_request['content-type']='application/x-www-form-urlencoded'

def is_it_solved(response):
  start=time.time()
  recaptacha_notification.sendWarningMessage("Waiting for response from Idealo","Testing on Site")
  print('Waiting from POST https://www.idealo.de for response')
  reponse=re.post('https://www.idealo.de',data={'g-recaptcha-response':response},headers=post_request)
  time_taken="\nTime taken : "+str((time.time()-start))
  if reponse.status_code==200:
    recaptacha_notification.sendSuccessMessage("Response : 200\nSounds Good! "+time_taken,"Pass")
  else:
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
      recaptacha_notification.sendInfoMessage("Recaptacha Solved by vendor"+time_taken)
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

def scrapeProductList(entries):

def main():
  for CATEGORY_LINK in CATEGORIES:
    CATEGORY_ID=str(int(CATEGORY_LINK.split('/')[-1].split('.')[0]))
    if logs_db.ifDataInLogs(CATEGORY_ID):continue
    notification.sendInfoMessage("Started category code: "+CATEGORY_ID+"\n"+CATEGORY_LINK)
    # print("Category: "+CATEGORY_ID)
    CATEGORY_JSON_API=os.getenv('CATEGORY_JSON_LINK').format(category_id=CATEGORY_ID)
    while True:
      json_page=re.get(CATEGORY_JSON_API)
      if json_page.status_code!=200:notification.sendErrorMessage("ERROR with category: "+CATEGORY_ID+"\nResoponse code : "+str(json_page.status_code),'Invalid Response Code')
      #Hande JSON Exception here
      try:
        JSON_RESULT=json_page.json()
      except 

      for product in JSON_RESULT['categoryJsonResults']["entries"]:
        dataDict={}
        try:
          if 'id' in product['link']['productLink']: dataDict['_id']=product['link']['productLink']['id']
          else: dataDict['_id']=product['link']['productLink']['Id']
        except TypeError:
          notification.sendErrorMessage("TypeError with product id of : "+CATEGORY_JSON_API,"Error")
          print("Error with : "+str(product))
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
        category_name=product['categoryName']
        scrape_product_page(dataDict)

      pagination=JSON_RESULT["categoryPagination"]
      if pagination['nextPageAjaxLink'] is None:break
      CATEGORY_JSON_API=pagination['nextPageAjaxLink']
    logs_db.store_data(CATEGORY_ID)
    notification.sendSuccessMessage("Category : "+category_name+" #"+str(CATEGORY_ID)+" is completed\n"+db.getCategoryValueCount(category_name))

if __name__ == "__main__":
    try:main()
    except Exception as p:notification.sendInfoMessage(str(p),"MAIN ERROR")


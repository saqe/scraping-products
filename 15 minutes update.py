from DataHandling.MongoHandler import MongoHandler
from _discord_.DiscordNotification import DiscordNotification
from dotenv import load_dotenv
from util.FileFlagHandler import FileFlagHandler

import os

load_dotenv()
flag=FileFlagHandler('15_MINUTES_UPDATE_LOG')

db=MongoHandler(os.getenv('MONGO_DB_API'))

notification=DiscordNotification(os.getenv('DISCORD_HOOK_15_MINUTES_UPDATE'))

categories=db.getCategories()
message="Total Records    :  "+str(db.count_records())+'\n'+"Total Categories :  "+str(len(categories))

if flag.isFileExists():
    previous_records=int(flag.getStatus())
    current_records=int(db.count_records())
    if previous_records!=current_records:
        notification.sendInfoMessage(str(message)+'\n New ='+str(current_records-previous_records),'DATABASE UPDATE')
else:notification.sendInfoMessage(str(message),'DATABASE UPDATE')
flag.setStatus(str(db.count_records()))
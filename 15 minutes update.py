from DataHandling.MongoHandler import MongoHandler
from _discord_.DiscordNotification import DiscordNotification
from dotenv import load_dotenv
from util.FileFlagHandler import FileFlagHandler
import os

load_dotenv()
flag=FileFlagHandler('15_MINUTES_UPDATE_LOG')

db=MongoHandler(os.getenv('MONGO_DB_API'))
db_secondary=MongoHandler(os.getenv('MONGO_DB_SECONDARY_API'))

notification=DiscordNotification(os.getenv('DISCORD_HOOK_15_MINUTES_UPDATE'))

categories=db.getCategories()
str(db.count_records())

total_record=db_secondary.count_records()+db.count_records()
total_categories=len(db_secondary.getCategories())+len(db.getCategories())

embed=notification.getEmbed()
embed.add_embed_field(name="Total Records", value=str(total_record), inline=False)
embed.add_embed_field(name="Total Categories", value=str(total_categories), inline=False)
embed.add_embed_field(name="Main DB", value=str(db.count_records()), inline=True)
embed.add_embed_field(name="Secondary DB", value=str(db_secondary.count_records()), inline=True)


if flag.isFileExists():
    previous_records=int(flag.getStatus())
    current_records=total_record
    if previous_records!=current_records:
        embed.add_embed_field(name="New records", value=(current_records-previous_records), inline=False)
        notification.sendEmbeddedMessage(embed)
else:notification.sendEmbeddedMessage(embed)

flag.setStatus(str(total_record))
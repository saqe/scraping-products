import discord
from discord.ext import commands
from util.FileFlagHandler import *
import os
from DataHandling.MongoHandler import MongoHandler

client = discord.Client()
flag=FileFlagHandler('.DISCORD_FILE_LAG')
db=MongoHandler()

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    print(message)
    if message.author == client.user:
        return

    content=message.content.lower().strip()
    
    if content.startswith("hello"):
        excute_flag=False
        await message.channel.send(f"Hi {message.author}, I am a bot. How are you doing?")

    elif content in ["stop"]:
        await message.channel.send("STOP Command Recived")
        flag.setDisable()

    elif content in ['start','done']:        
        await message.channel.send("Start/Done Command Recived")
        flag.setEnable() 

    elif "count" in content:
        await message.channel.send("Total records :"+str(db.count_records()))
    
    elif content=="status":
        await message.channel.send("STATUS : "+str(flag.getStatus()))

    elif content=="--help":
        embed=discord.Embed(title="> Commands", description="These are the list of commands for getting help from chat bot ")
        embed.add_field(name="start or !done", value="To start the process", inline=True)
        embed.add_field(name="stop", value="To stop the scraping process", inline=True)
        embed.add_field(name="status", value="Getting know about the status of the scraping", inline=True)
        await message.channel.send(embed=embed)
    
    elif "?" in content:
        await message.channel.send("> Need any help?")
        await message.channel.send("""```Commands starts with ! symbol\ntype --help if you need any help ```""")

client.run('Njk5MzQ0ODMxMDg4MTY0ODg0.XpTDmw.kS9UwQnhoVP4FF1aEGHG7ZLNTuI')
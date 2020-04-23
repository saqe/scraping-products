from discord_webhook import DiscordWebhook, DiscordEmbed
from datetime import datetime

class DiscordNotification:
    def __init__(self,hook_link):
        self.hookLink=hook_link
        self.COLOR_INFORMATION=6013150
        self.COLOR_Error=14242639
        self.COLOR_Warning=15773006
        self.COLOR_Success=6076508

    def setWebHook(self,hook_link):
        self.hookLink=hook_link

    def sendInfoMessage(self,desc,title="INFORMATION ✌🏿"):
        self.sendMessage(title,desc,self.COLOR_INFORMATION)

    def sendErrorMessage(self,desc,title="ERROR 😕"):
        self.sendMessage(title,desc,self.COLOR_Error)
    
    def sendWarningMessage(self,desc,title="📛 WARNING 🙄"):
        self.sendMessage(title,desc,self.COLOR_Warning)

    def sendSuccessMessage(self,desc,title="💯 SUCCESS 🤩"):
        self.sendMessage(title,desc,self.COLOR_Success)

    def sendEmbeddedMessage(self,embedded_message):
        webhook=DiscordWebhook(url=self.hookLink)
        webhook.add_embed(embedded_message)
        webhook.execute()

    def getEmbed(self):
        return DiscordEmbed()

    def sendMessage(self,msg_title,desc,side_color):
        webhook=DiscordWebhook(url=self.hookLink)
        embed = DiscordEmbed(title=msg_title, description=datetime.now().strftime("%I:%M %p\n")+desc, color=side_color)
        webhook.add_embed(embed)
        webhook.execute()
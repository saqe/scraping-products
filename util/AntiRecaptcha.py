from python_anticaptcha import AnticaptchaClient, NoCaptchaTaskProxylessTask
from python_anticaptcha.exceptions import AnticaptchaException
from _discord_.DiscordNotification import DiscordNotification
import time
class AntiRecaptcha:
    def __init__(self,client,site_key,url):
        self.client = AnticaptchaClient(client)
        self.task = NoCaptchaTaskProxylessTask(url, site_key)
        self.notify=None

    def set_discord_channel(self,webhooks):
        self.notify=DiscordNotification(webhooks)

    def getResponse(self):
        while True:
            try:   
                self.job = self.client.createTask(self.task)
                self.job.join()
                response=self.job.get_solution_response()
                break        
            except AnticaptchaException as exception:
                self.notify.sendErrorMessage(str(exception),"AnticaptchaException")
                self.incorrect()
                time.sleep(1)
                self.notify.sendInfoMessage("Trying again with by creating a new , ")
                continue
        return response

    def incorrect(self):
        self.job.report_incorrect_recaptcha()
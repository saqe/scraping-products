from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os 
from dotenv import load_dotenv
load_dotenv()
class GDriveHandler:
    def __init__(self):
        self.gauth = GoogleAuth()
    
    def authenticate(self,credentials_file_location):
        self.gauth.LoadCredentialsFile(credentials_file_location)
        if self.gauth.credentials is None:print("Some error")
        elif self.gauth.access_token_expired:self.gauth.Refresh()
        else: self.gauth.Authorize()

        self.gauth.SaveCredentialsFile(credentials_file_location)        
        self.drive = GoogleDrive(self.gauth)
        return True
    
    def setGDriveFolderId(self,folder_id):
        self.folder_id=folder_id
    
    def uploadfile(self,file_location,file_name):
        drive_file = self.drive.CreateFile({"parents": [{"kind": "drive#fileLink", "id": self.folder_id}]})
        drive_file.SetContentFile(file_location)
        drive_file['title']=file_name
        drive_file.Upload()
        print(drive_file['originalFilename'],drive_file['id'])
        return drive_file


gdrive=GDriveHandler()
result=gdrive.authenticate(os.getenv('GDRIVE_CRENTIAL_LOCATION'))
gdrive.setGDriveFolderId(os.getenv('GDRIVE_FOLDER_ID'))

print(result)


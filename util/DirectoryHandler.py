import os
class FileDirectory:
    @staticmethod
    def checkAndCreatePath(directory):
        directory=directory.replace('/','')
        if not os.path.exists(directory):
            os.makedirs(directory)
            print("[>] "+directory+" Folder Created.")
            return True
        return False
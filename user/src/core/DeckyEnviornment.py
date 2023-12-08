import json
import os


class DeckyEnviornment:

    filepath = '/home/deck/homebrew/settings/SPGMTweaks/settings.json'
    _cached_stamp = 0

    def getEnv(appId: any):
        appIdStr = str(appId)
        envVars = {}
        try:
            if os.path.exists(DeckyEnviornment.filepath):
                f = open(DeckyEnviornment.filepath)
                jsonFile = dict(json.load(f))
                for key in jsonFile:
                    if str(key).startswith(appIdStr + "."):
                        variable_name = str(key).removeprefix(appIdStr + ".")
                        envVars[variable_name] = jsonFile[key]
        except Exception as e:
            print(e)
            #raise e
            #print('unreadable')
            pass

        return envVars
        
    def hasUpdate():
        hasUpdated = False

        try:
            if os.path.exists(DeckyEnviornment.filepath):
                stamp = os.stat(DeckyEnviornment.filepath).st_mtime
                if stamp != DeckyEnviornment._cached_stamp:
                   DeckyEnviornment._cached_stamp = stamp
                   hasUpdated = True
        except Exception as e:
            pass

        return hasUpdated
    
    def init():
        DeckyEnviornment.hasUpdate()

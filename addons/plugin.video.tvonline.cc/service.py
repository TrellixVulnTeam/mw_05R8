'''
author: kinkin
'''

import time,datetime
import xbmc
import xbmcaddon
import settings
from datetime import date, timedelta
ADDON = settings.addon()

class AutoUpdater:             
    def runProgram(self):
        self.last_run = 0
        while not xbmc.abortRequested:
            if settings.enable_subscriptions():
                try:
                    next_run  = datetime.datetime.fromtimestamp(time.mktime(time.strptime(ADDON.getSetting('service_time').encode('utf-8', 'replace'), "%Y-%m-%d %H:%M:%S")))
                    now = datetime.datetime.now()
                    if now > next_run:
                        xbmc.log('[TVonline] Clearing aged cache files')
                        xbmc.executebuiltin('RunPlugin(plugin://plugin.video.tvonline.cc/?name=service&url=service&mode=26&list=service)')
                        if xbmc.Player().isPlaying() == False:
                            if xbmc.getCondVisibility('Library.IsScanningVideo') == False:      
                                xbmc.log('[TVonline] Refreshing subscriptions')
                                time.sleep(1)
                                xbmc.executebuiltin('RunPlugin(plugin://plugin.video.tvonline.cc/?name=service&url=service&mode=17&list=service)') 
                                time.sleep(1)
                                self.last_run = now
                                ADDON.setSetting('service_time', str(datetime.datetime.now() + timedelta(hours=12)).split('.')[0])
                                xbmc.log("[TVonline] Subscriptions and Library updated. Next run at " + ADDON.getSetting('service_time'))
                        else:
                            xbmc.log("[TVonline] Player is running, waiting until finished")
                except:
                    pass
            xbmc.sleep(1000)


xbmc.log("[TVonline] Subscription service starting...")
AutoUpdater().runProgram()

# -*- coding: utf-8 -*-
#------------------------------------------------------------
# http://www.youtube.com/user/epicmealtime
#------------------------------------------------------------
# License: GPL (http://www.gnu.org/licenses/gpl-3.0.html)
# Based on code from youtube addon
#------------------------------------------------------------

import os
import sys
import plugintools
import xbmc,xbmcaddon
from addon.common.addon import Addon

addonID = 'plugin.video.NHLVideo'
addon = Addon(addonID, sys.argv)
local = xbmcaddon.Addon(id=addonID)
icon = local.getAddonInfo('icon')

YOUTUBE_CHANNEL_ID = "NHLVideo"

# Entry point
def run():
    plugintools.log("NHLVideo.run")
    
    # Get params
    params = plugintools.get_params()
    
    if params.get("action") is None:
        main_list(params)
    else:
        action = params.get("action")
        exec action+"(params)"
    
    plugintools.close_item_list()

# Main menu
def main_list(params):
    plugintools.log("NHLVideo.main_list "+repr(params))

    plugintools.add_item( 
        #action="", 
        title="National Hockey League",
        url="plugin://plugin.video.youtube/user/"+YOUTUBE_CHANNEL_ID+"/",
        thumbnail=icon,
        folder=True )


run()
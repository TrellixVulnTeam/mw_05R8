'''
    Ice Channel
'''

from entertainment.plugnplay.interfaces import LiveTVIndexer
from entertainment.plugnplay import Plugin
from entertainment import common

class more4(LiveTVIndexer):
    implements = [LiveTVIndexer]
    
    display_name = 'More4'
    
    name = 'more4'
    
    import xbmcaddon
    import os
    addon_id = 'script.icechannel.extn.uk'
    addon = xbmcaddon.Addon(addon_id)
    img = "http://static.filmon.com/couch/channels/97/extra_big_logo.png"
    
    regions = [ 
            {
                'name':'United Kingdom', 
                'img':addon.getAddonInfo('icon'), 
                'fanart':addon.getAddonInfo('fanart')
                }, 
        ]
        
    languages = [ 
        {'name':'English', 'img':'', 'fanart':''}, 
        ]
        
    genres = [ 
        {'name':'Entertainment', 'img':'', 'fanart':''} 
        ]
    
    addon = None
    

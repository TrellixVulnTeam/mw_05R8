'''
    Ice Channel
'''

from entertainment.plugnplay.interfaces import LiveTVIndexer
from entertainment.plugnplay.interfaces import LiveTVSource
from entertainment.plugnplay import Plugin
from entertainment import common

class ideal_world(LiveTVIndexer, LiveTVSource):
    implements = [LiveTVIndexer, LiveTVSource]
    
    display_name = "Ideal World"
    
    name = 'ideal_world'
    
    base_url = 'http://www.idealworld.tv/ShowGridView.aspx'
    
    import xbmcaddon
    import os
    addon_id = 'script.icechannel.extn.uk'
    addon = xbmcaddon.Addon(addon_id)
    img = os.path.join( addon.getAddonInfo('path'), 'resources', 'images', name + '.png' )
    
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
        {'name':'Shopping', 'img':'', 'fanart':''} 
        ]
    
    addon = None
    
    def GetFileHosts(self, id, other_names, region, language, list, lock, message_queue):
        if id == self.name:
            self.AddLiveLink(list, self.display_name, self.base_url, language='English', region='United Kingdom')
            
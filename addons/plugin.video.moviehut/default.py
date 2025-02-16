import urllib,urllib2,re,xbmcplugin,xbmcgui,urlresolver,sys,xbmc,xbmcaddon,os,urlparse
from t0mm0.common.addon import Addon
from metahandler import metahandlers

addon_id = 'plugin.video.moviehut'
selfAddon = xbmcaddon.Addon(id=addon_id)
addon = Addon(addon_id, sys.argv)
fanart = xbmc.translatePath(os.path.join('special://home/addons/' + addon_id , 'fanart.jpg'))
icon = xbmc.translatePath(os.path.join('special://home/addons/' + addon_id, 'icon.png'))
metaset = selfAddon.getSetting('enable_meta')
addon = Addon(addon_id, sys.argv)

def CATEGORIES():
        addDir2('Featured','http://www.moviehut.co/watch-recent-featured-movies.html',1,icon,fanart)
        addDir2('Recently Added','http://www.moviehut.co/',1,icon,fanart)
        addDir2('Recently Updated','http://www.moviehut.co/watch-update-movies.html',1,icon,fanart)
        addDir2('Popular','http://www.moviehut.co/watch-popular-movies.html',1,icon,fanart)
        addDir2('Highest Rated','http://www.moviehut.co/watch-rating-movies.html',1,icon,fanart)
        addDir2('Genres','http://www.moviehut.co/',4,icon,fanart)
        addDir2('Years','http://www.moviehut.co/',5,icon,fanart)
        addDir2('Search','http://www.moviehut.co/',3,icon,fanart)
                
def GETMOVIES(url,name):
        metaset = selfAddon.getSetting('enable_meta')
        link = open_url(url)
        match=re.compile('<a href="(.+?)"><img alt=".+?" title="(.+?)"').findall(link)
        for url,name in match:
                name=cleanHex(name)
                if metaset=='false':
                        try:
                                addDir2(name,url,2,icon,fanart)
                        except:pass
                else:
                        try:
                                addDir(name,url,2,icon,len(match),isFolder=True)
                        except:pass
        if metaset=='true':
                setView('movies', 'MAIN')
        else: xbmc.executebuiltin('Container.SetViewMode(50)')

def GETLINKS(url,name,iconimage):
        selfAddon.setSetting('namestore',name)
        link = open_url(url)
        match=re.compile('target="_blank" href="(.+?)">Watch Link .+?</a>').findall(link)
        for url in match:
                if urlresolver.HostedMediaFile(url).valid_url():
                        host=url.split('/')[2].replace('www.','').capitalize()
                        addLink(host,url,100,iconimage,fanart)
                                      
def SEARCH():
    search_entered =''
    keyboard = xbmc.Keyboard(search_entered, 'Search HuluBox')
    keyboard.doModal()
    if keyboard.isConfirmed():
        search_entered = keyboard.getText().replace(' ','-')
    if len(search_entered)>1:
        url = 'http://www.moviehut.co/bestmatch-search-'+search_entered+'.html'
        link = open_url(url)
        GETMOVIES(url,name)

def YEARS(url):
        link = open_url(url)
        gensec=re.compile('<div id="yearBox"(.+?)</div>',re.DOTALL).findall(link)[0]
        match=re.compile('<a href="(.+?)">(.+?)</a>').findall(gensec)
        for url,name in match:
                url='http://www.moviehut.co/'+url
                print url
                addDir2(name,url,1,icon,fanart)
        
def GENRES(url):
        link = open_url(url)
        gensec=re.compile('<div id="genBox" class="genBox">(.+?)</div>',re.DOTALL).findall(link)[0]
        match=re.compile('<a href="(.+?)">(.+?)</a>').findall(gensec)
        for url,name in match:
                addDir2(name,url,1,icon,fanart)
                
def PLAYLINK(name,url,iconimage):
        name=selfAddon.getSetting('namestore')
        stream_url=urlresolver.resolve(url)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage); liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
        xbmc.Player ().play(stream_url, liz, False)
        
def cleanHex(text):
    def fixup(m):
        text = m.group(0)
        if text[:3] == "&#x": return unichr(int(text[3:-1], 16)).encode('utf-8')
        else: return unichr(int(text[2:-1])).encode('utf-8')
    return re.sub("(?i)&#\w+;", fixup, text.decode('ISO-8859-1').encode('utf-8'))

def get_params():
        param=[]
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
                params=sys.argv[2]
                cleanedparams=params.replace('?','')
                if (params[len(params)-1]=='/'):
                        params=params[0:len(params)-2]
                pairsofparams=cleanedparams.split('&')
                param={}
                for i in range(len(pairsofparams)):
                        splitparams={}
                        splitparams=pairsofparams[i].split('=')
                        if (len(splitparams))==2:
                                param[splitparams[0]]=splitparams[1]
                               
        return param

def addDir2(name,url,mode,iconimage,fanart,description=''):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)+"&description="+urllib.quote_plus(description)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name, 'plot': description } )
        liz.setProperty('fanart_image', fanart)
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok

def addLink(name,url,mode,iconimage,description=''):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)+"&description="+urllib.quote_plus(description)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name, "Plot": description} )
        liz.setProperty('fanart_image', fanart)
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
        return ok

def addDir(name,url,mode,iconimage,itemcount,isFolder=False):
        if metaset=='true':
          if not 'COLOR' in name:
            splitName=name.partition('(')
            simplename=""
            simpleyear=""
            if len(splitName)>0:
                simplename=splitName[0]
                simpleyear=splitName[2].partition(')')
            if len(simpleyear)>0:
                simpleyear=simpleyear[0]
            mg = metahandlers.MetaData()
            meta = mg.get_meta('movie', name=simplename ,year=simpleyear)
            u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)
            ok=True
            liz=xbmcgui.ListItem(name, iconImage=meta['cover_url'], thumbnailImage=meta['cover_url'])
            liz.setInfo( type="Video", infoLabels= meta )
            liz.setProperty("IsPlayable","true")
            contextMenuItems = []
            contextMenuItems.append(('Movie Information', 'XBMC.Action(Info)'))
            liz.addContextMenuItems(contextMenuItems, replaceItems=True)
            if not meta['backdrop_url'] == '': liz.setProperty('fanart_image', meta['backdrop_url'])
            else: liz.setProperty('fanart_image', fanart)
            ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=isFolder,totalItems=itemcount)
            return ok
        else:
            u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)+"&description="+urllib.quote_plus(description)
            ok=True
            liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
            liz.setInfo( type="Video", infoLabels={ "Title": name } )
            liz.setProperty('fanart_image', fanart)
            liz.setProperty("IsPlayable","true")
            ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=isFolder)
            return ok
        
def open_url(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    response = urllib2.urlopen(req)
    link=response.read()
    response.close()
    return link

def setView(content, viewType):
    if content:
        xbmcplugin.setContent(int(sys.argv[1]), content)
    if selfAddon.getSetting('auto-view')=='true':
        xbmc.executebuiltin("Container.SetViewMode(%s)" % selfAddon.getSetting(viewType) )

params=get_params(); url=None; name=None; mode=None; site=None; iconimage=None
try: site=urllib.unquote_plus(params["site"])
except: pass
try: url=urllib.unquote_plus(params["url"])
except: pass
try: name=urllib.unquote_plus(params["name"])
except: pass
try: mode=int(params["mode"])
except: pass
try: iconimage=urllib.unquote_plus(params["iconimage"])
except: pass

print "Site: "+str(site); print "Mode: "+str(mode); print "URL: "+str(url); print "Name: "+str(name)
print params

if mode==None or url==None or len(url)<1: CATEGORIES()
elif mode==1: GETMOVIES(url,name)
elif mode==2: GETLINKS(url,name,iconimage)
elif mode==3: SEARCH()
elif mode==4: GENRES(url)
elif mode==5: YEARS(url)
elif mode==100: PLAYLINK(name,url,iconimage)

xbmcplugin.endOfDirectory(int(sys.argv[1]))


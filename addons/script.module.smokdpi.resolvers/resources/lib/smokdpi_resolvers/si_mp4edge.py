"""
    Kodi urlresolver plugin
    Copyright (C) 2014  smokdpi

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""


from t0mm0.common.net import Net
from urlresolver.plugnplay.interfaces import UrlResolver
from urlresolver.plugnplay.interfaces import PluginSettings
from urlresolver.plugnplay import Plugin
from urlresolver import common
import urllib
import re


class AaaaMp4EdgeResolver(Plugin, UrlResolver, PluginSettings):
    implements = [UrlResolver, PluginSettings]
    name = "si_mp4edge.com"
    domains = ["mp4edge.com"]
    
    def __init__(self):
        p = self.get_setting('priority') or 100
        self.priority = int(p)
        self.net = Net()
        self.pattern = 'http://((?:.*?)mp4edge\.com)/stream/([0-9a-zA-Z]+)'
        self.user_agent = common.IE_USER_AGENT
        self.net.set_user_agent(self.user_agent)
        self.headers = {'User-Agent': self.user_agent}

    def get_url(self, host, media_id):
        return 'http://%s/stream/%s' % (host, media_id)
    
    def get_host_and_id(self, url):
        r = re.search(self.pattern, url)
        if r: return r.groups()
        else: return False
    
    def valid_url(self, url, host):
        if self.get_setting('enabled') == 'false': return False
        return re.match(self.pattern, url) or host in self.domains
    
    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        self.headers['Referer'] = web_url
        html = self.net.http_GET(web_url, headers=self.headers).content
        r = re.search('file\s*:\s*["\'](.+?)["\']', html)
        if r:
            return self.__add_headers_for_kodi(r.group(1))
        else:
            raise UrlResolver.ResolverError('File not found')

    def __add_headers_for_kodi(self, url):
        _referer = urllib.quote_plus('http://%s/' % self.domains[0])
        _user_agent = urllib.quote_plus(self.net._user_agent)
        _connection_timeout = '60'
        _cookies = ''
        for _cookie in self.net._cj:
            _cookies += urllib.quote_plus('%s=%s;' % (_cookie.name, _cookie.value))
        if _cookies:
            return '%s|Referer=%s&User-Agent=%s&Connection-Timeout=%s&Cookie=%s' % \
                   (url, _referer, _user_agent, _connection_timeout, _cookies)
        else:
            return '%s|Referer=%s&User-Agent=%s&Connection-Timeout=%s' % \
                   (url, _referer, _user_agent, _connection_timeout)
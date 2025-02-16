"""
    SALTS XBMC Addon
    Copyright (C) 2014 tknorris

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
import scraper
import urlparse
import re
from salts_lib import kodi
import time
import json
from salts_lib import log_utils
from salts_lib.trans_utils import i18n
from salts_lib.constants import VIDEO_TYPES
from salts_lib.constants import FORCE_NO_MATCH
from salts_lib.constants import QUALITIES
from salts_lib.constants import XHR

BASE_URL = 'http://www.moviesplanet.is'
QUALITY_MAP = {'HD': QUALITIES.HD720}

class MoviesPlanet_Scraper(scraper.Scraper):
    base_url = BASE_URL

    def __init__(self, timeout=scraper.DEFAULT_TIMEOUT):
        self.timeout = timeout
        self.base_url = kodi.get_setting('%s-base_url' % (self.get_name()))
        self.username = kodi.get_setting('%s-username' % (self.get_name()))
        self.password = kodi.get_setting('%s-password' % (self.get_name()))

    @classmethod
    def provides(cls):
        return frozenset([VIDEO_TYPES.TVSHOW, VIDEO_TYPES.EPISODE, VIDEO_TYPES.MOVIE])

    @classmethod
    def get_name(cls):
        return 'MoviesPlanet'

    def resolve_link(self, link):
        return link

    def format_source_label(self, item):
        return '[%s] %s' % (item['quality'], item['host'])

    def get_sources(self, video):
        source_url = self.get_url(video)
        sources = []
        if source_url and source_url != FORCE_NO_MATCH:
            url = urlparse.urljoin(self.base_url, source_url)
            html = self._http_get(url, cache_limit=.5)
            for match in re.finditer("embeds\[(\d+)\]\s*=\s*'([^']+)", html):
                match = re.search('src="([^"]+)', match.group(2))
                if match:
                    html = self._http_get(match.group(1), cache_limit=0)
                    match = re.search('sources\s*:\s*\[(.*?)\]', html, re.DOTALL)
                    if match:
                        for match in re.finditer('''['"]*file['"]*\s*:\s*['"]*([^'"]+).*?['"]*label['"]*\s*:\s*['"]*([^'"]+)''', match.group(1), re.DOTALL):
                            stream_url, label = match.groups()
                            if 'download.php' in stream_url:
                                redir_html = self._http_get(stream_url, allow_redirect=False, cache_limit=0)
                                if stream_url.startswith('http'): stream_url = redir_html
                
                            host = self._get_direct_hostname(stream_url)
                            if host == 'gvideo':
                                quality = self._gv_get_quality(stream_url)
                            else:
                                quality = QUALITY_MAP.get(label, QUALITIES.HIGH)
                            stream_url += '|User-Agent=%s' % (self._get_ua())
                            source = {'multi-part': False, 'url': stream_url, 'host': host, 'class': self, 'quality': quality, 'views': None, 'rating': None, 'direct': True}
                            sources.append(source)

        return sources

    def get_url(self, video):
        return super(MoviesPlanet_Scraper, self)._default_get_url(video)

    def search(self, video_type, title, year):
        results = []
        search_url = urlparse.urljoin(self.base_url, '/ajax/search.php')
        timestamp = int(time.time() * 1000)
        query = {'q': title, 'limit': '100', 'timestamp': timestamp, 'verifiedCheck': ''}
        html = self._http_get(search_url, data=query, headers=XHR, cache_limit=1)
        if video_type in [VIDEO_TYPES.TVSHOW, VIDEO_TYPES.EPISODE]:
            media_type = 'TV SHOW'
        else:
            media_type = 'MOVIE'

        if html:
            try:
                js_data = json.loads(html)
            except ValueError:
                log_utils.log('No JSON returned: %s: %s' % (search_url, html), log_utils.LOGWARNING)
            else:
                for item in js_data:
                    if item['meta'].upper().startswith(media_type):
                        result = {'title': item['title'], 'url': self._pathify_url(item['permalink']), 'year': ''}
                        results.append(result)

        return results

    def _get_episode_url(self, show_url, video):
        episode_pattern = 'href="([^"]+/season/%s/episode/%s/?)"' % (video.season, video.episode)
        return super(MoviesPlanet_Scraper, self)._default_get_episode_url(show_url, video, episode_pattern)

    @classmethod
    def get_settings(cls):
        settings = super(MoviesPlanet_Scraper, cls).get_settings()
        name = cls.get_name()
        settings.append('         <setting id="%s-username" type="text" label="     %s" default="" visible="eq(-4,true)"/>' % (name, i18n('username')))
        settings.append('         <setting id="%s-password" type="text" label="     %s" option="hidden" default="" visible="eq(-5,true)"/>' % (name, i18n('password')))
        return settings

    def _http_get(self, url, data=None, headers=None, allow_redirect=True, cache_limit=8):
        # return all uncached blank pages if no user or pass
        if not self.username or not self.password:
            return ''

        html = super(MoviesPlanet_Scraper, self)._cached_http_get(url, self.base_url, self.timeout, data=data, headers=headers, allow_redirect=allow_redirect, cache_limit=cache_limit)
        if re.search('Please Register or Login', html, re.I):
            log_utils.log('Logging in for url (%s)' % (url), log_utils.LOGDEBUG)
            self.__login()
            html = super(MoviesPlanet_Scraper, self)._cached_http_get(url, self.base_url, self.timeout, data=data, headers=headers, allow_redirect=allow_redirect, cache_limit=0)
        return html

    def __login(self):
        url = urlparse.urljoin(self.base_url, '/login')
        data = {'username': self.username, 'password': self.password, 'action': 'login'}
        html = super(MoviesPlanet_Scraper, self)._cached_http_get(url, self.base_url, self.timeout, data=data, headers=XHR, cache_limit=0)
        if 'incorrect login' in html.lower():
            raise Exception('moviesplanet login failed')

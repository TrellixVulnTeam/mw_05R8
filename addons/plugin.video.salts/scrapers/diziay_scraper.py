# -*- coding: utf-8 -*-
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
import re
import urlparse
import urllib
from salts_lib import dom_parser
from salts_lib import log_utils
from salts_lib.constants import VIDEO_TYPES
from salts_lib.constants import FORCE_NO_MATCH
from salts_lib.constants import XHR
from salts_lib import kodi

BASE_URL = 'http://diziay.com'
SEASON_URL = '/posts/filmgonder.php?action=sezongets'

class Diziay_Scraper(scraper.Scraper):
    base_url = BASE_URL

    def __init__(self, timeout=scraper.DEFAULT_TIMEOUT):
        self.timeout = timeout
        self.base_url = kodi.get_setting('%s-base_url' % (self.get_name()))

    @classmethod
    def provides(cls):
        return frozenset([VIDEO_TYPES.TVSHOW, VIDEO_TYPES.EPISODE])

    @classmethod
    def get_name(cls):
        return 'Diziay'

    def resolve_link(self, link):
        return link

    def format_source_label(self, item):
        label = '[%s] %s' % (item['quality'], item['host'])
        if 'subs' in item and item['subs']:
            label += ' (Turkish subtitles)'
        return label

    def get_sources(self, video):
        source_url = self.get_url(video)
        hosters = []
        if source_url and source_url != FORCE_NO_MATCH:
            page_url = urlparse.urljoin(self.base_url, source_url)
            html = self._http_get(page_url, cache_limit=1)
            fragment = dom_parser.parse_dom(html, 'div', {'class': 'player'})
            if fragment:
                iframe_url = dom_parser.parse_dom(fragment[0], 'iframe', ret='src')
                if iframe_url:
                    html = self._http_get(iframe_url[0], cache_limit=.5)

                    # if captions exist, then they aren't hardcoded
                    if re.search('kind\s*:\s*"captions"', html):
                        subs = False
                    else:
                        subs = True
                        
                    for name, stream_url in self.__get_stream_cookies().items():
                        if re.match('source_\d+p?', name):
                            stream_url = urllib.unquote(stream_url)
                            if self._get_direct_hostname(stream_url) == 'gvideo':
                                quality = self._gv_get_quality(stream_url)
                                hoster = {'multi-part': False, 'host': self._get_direct_hostname(stream_url), 'class': self, 'quality': quality, 'views': None, 'rating': None, 'url': stream_url, 'direct': True, 'subs': subs}
                                hosters.append(hoster)
    
        return hosters

    def __get_stream_cookies(self):
        cj = self._set_cookies(self.base_url, {})
        cookies = {}
        for cookie in cj:
            cookies[cookie.name] =cookie.value
        return cookies

    def get_url(self, video):
        return super(Diziay_Scraper, self)._default_get_url(video)

    def _get_episode_url(self, show_url, video):
        url = urlparse.urljoin(self.base_url, show_url)
        html = self._http_get(url, cache_limit=24)
        show_id = dom_parser.parse_dom(html, 'div', {'id': 'icerikid'}, ret='value')
        if show_id:
            data = {'sezon_id': video.season, 'dizi_id': show_id[0], 'tip': 'dizi', 'bolumid': ''}
            episode_pattern = 'href="([^"]+/[^"]*%s-sezon-%s-bolum[^"]*)"' % (video.season, video.episode)
            title_pattern = 'href="(?P<url>[^"]*-\d+-sezon-\d+-bolum[^"]*)[^>]*>.*?class="realcuf">(?P<title>[^<]*)'
            return super(Diziay_Scraper, self)._default_get_episode_url(SEASON_URL, video, episode_pattern, title_pattern, data=data, headers=XHR)

    def search(self, video_type, title, year):
        html = self._http_get(self.base_url, cache_limit=8)
        results = []
        fragment = dom_parser.parse_dom(html, 'div', {'class': '[^"]*dizis[^"]*'})
        norm_title = self._normalize_title(title)
        if fragment:
            for match in re.finditer('href="([^"]+)[^>]*>([^<]+)', fragment[0]):
                url, match_title = match.groups()
                if norm_title in self._normalize_title(match_title):
                    result = {'url': self._pathify_url(url), 'title': match_title, 'year': ''}
                    results.append(result)

        return results

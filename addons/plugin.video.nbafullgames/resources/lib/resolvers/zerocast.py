# -*- coding: utf-8 -*-

'''
    Genesis Add-on
    Copyright (C) 2015 lambda

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
'''


import re,urlparse,base64
from resources.lib.modules import client


def resolve(url):
    try:
        try: referer = urlparse.parse_qs(urlparse.urlparse(url).query)['referer'][0]
        except: referer = url

        page = urlparse.parse_qs(urlparse.urlparse(url).query)['a'][0]
        page = 'http://zerocast.tv/embed.php?a=%s&id=&width=640&height=480&autostart=true&strech=exactfit' % page

        result = client.request(page, referer=referer)

        result = client.request(page, referer=referer, close=False)
        result = re.compile('url\s*=\s*"(.*?)"').findall(result)[0]
        result = base64.b64decode(result)

        chunk = client.request(result)
        chunk = re.compile('(chunklist_.+)').findall(chunk)[0]

        url = result.split('.m3u8')[0].rsplit('/', 1)[0] + '/' + chunk

        return url
    except:
        return



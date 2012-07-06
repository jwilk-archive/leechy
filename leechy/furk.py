# encoding=UTF-8

# Copyright © 2012 Jakub Wilk <jwilk@jwilk.net>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the “Software”), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import re
_xspf_search = re.compile('<a class="button-large button-play" href="(http://[^"]+)">Play<').search
_wait_search = re.compile('You need to wait ([0-9]+) seconds').search
_auth_search = re.compile('DL:([a-z0-9]+[.]rapidshare[.]com),([0-9A-F]+),([0-9]+)').search
del re

import os
import urllib
import urlparse
import xml.etree.cElementTree as etree

from leechy import Browser

class Browser(Browser):

    pattern = r'https?://www.furk.net/dt/[0-9a-f]+'

    def download(self):
        response = self.open(self.start_uri)
        content = response.read()
        xspf_match = _xspf_search(content)
        if xspf_match is None:
            self.report_api_error('xspf')
        url = xspf_match.group(1)
        response = self.open(url)
        content = response.read()
        content = etree.fromstring(content)
        for elem in content.findall('.//{http://xspf.org/ns/0/}location'):
            url = elem.text or ''
            if not url.startswith('http://'):
                raise ValueError
            path = urllib.unquote(urlparse.urlparse(url).path)
            target = path.split('/')[-1]
            if os.path.exists(target):
                self.log_info('Nothing to do.')
                continue
            self.wget(url, target)
        return
        yield

# vim:ts=4 sw=4 et

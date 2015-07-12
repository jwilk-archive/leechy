# encoding=UTF-8

# Copyright © 2009, 2010, 2012 Jakub Wilk <jwilk@jwilk.net>
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
_wait_search = re.compile('You need to wait ([0-9]+) seconds').search
_auth_search = re.compile('DL:([a-z0-9]+[.]rapidshare[.]com),([0-9A-F]+),([0-9]+)').search
del re

from leechy import Browser

class Browser(Browser):

    pattern = r'^https?://(?:www[.])?rapidshare[.]com/files/[0-9]+/'

    def download(self):
        import urlparse
        import os
        _, _, target, _, _, _ = urlparse.urlparse(self.start_uri)
        ident, target = target.split('/')[-2:]
        if os.path.exists(target):
            self.log_info('Nothing to do.')
            return
        response = self.open(self.start_uri)
        while 1:
            url = 'http://api.rapidshare.com/cgi-bin/rsapi.cgi?sub=download&fileid=%s&filename=%s' % (ident, target)
            response = self.open(url)
            content = response.read()
            m = _wait_search(content)
            if m is not None:
                [seconds] = m.groups()
                seconds = int(seconds)
                yield seconds
                continue
            break
        m = _auth_search(content)
        if m is None:
            if 'more files from your IP' in content:
                self.report_simultaneous_download()
            self.report_api_error('auth')
        host, magic, wait = m.groups()
        wait = int(wait)
        yield wait
        url = 'http://%s/cgi-bin/rsapi.cgi' % host
        data = 'sub=download&fileid=%s&filename=%s&dlauth=%s' % (ident, target, magic)
        self.wget(url, target, data)

# vim:ts=4 sts=4 sw=4 et

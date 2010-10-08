# encoding=UTF-8

# Copyright © 2010 Jakub Wilk <jwilk@jwilk.net>
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

from leechy import Browser

import re
_regular_download_re = re.compile(r'http://www.filesonic.com/download-free/[0-9]+')
_wait_search = re.compile(r'Please wait <strong id="countdown">([0-9]+):([0-9]+)</strong> to download this file[.]').search
_uri_search = re.compile('downloadUrl = "(http://[a-z0-9]+[.]filesonic[.]com/download/[^"]+)"').search
del re

class Browser(Browser):

    pattern = r'^http://www[.]filesonic[.]com/file/(?:r[0-9]+/)?[0-9]+/[^/]+$'

    def download(self):
        import urlparse
        import os
        _, _, target, _, _, _ = urlparse.urlparse(self.start_uri)
        target = target.split('/')[-1]
        if os.path.exists(target):
            self.log_info('Nothing to do.')
            return
        self.open(self.start_uri)
        response = self.follow_link(url_regex=_regular_download_re)
        content = response.read()
        m = _uri_search(content)
        if m is None:
            self.report_api_error('uri')
        uri = m.group(1)
        m = _wait_search(content)
        if m is None:
            self.report_api_error('wait')
        seconds = int(m.group(1)) * 60 + int(m.group(2))
        yield seconds
        self.wget(uri, target)
        return

# vim:ts=4 sw=4 et

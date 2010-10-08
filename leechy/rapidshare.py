# encoding=UTF-8

# Copyright © 2009, 2010 Jakub Wilk <jwilk@jwilk.net>
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
_wait1_search = re.compile(r'(?:will have to wait|try again in about) (\d+) minutes').search
_wait2_search = re.compile(r'^var c=(\d+);', re.MULTILINE).search
_overloaded_search = re.compile(r'Unfortunately right now our servers are overloaded').search
_race_search = re.compile(r'already downloading a file').search
_uri_search = re.compile(r'form name="dlf" action="([^"]+)"').search
del re

from leechy import Browser

class Browser(Browser):

    pattern = r'^http://rapidshare[.]com/files/[0-9]+/'

    def download(self):
        import urlparse
        import os
        _, _, target, _, _, _ = urlparse.urlparse(self.start_uri)
        target = target.split('/')[-1]
        if os.path.exists(target):
            self.log_info('Nothing to do.')
            return
        response = self.open(self.start_uri)
        try:
            self.forms().next()
        except StopIteration:
            content = response.read()
            if 'The file could not be found' in content:
                self.report_file_not_found()
            elif 'is momentarily not available' in content:
                self.report_temporary_failure()
            else:
                self.report_api_error('noforms')
        self.select_form(nr=1)
        response = self.submit()
        content = response.read()
        while True:
            if _overloaded_search(content):
                yield 300 # FIXME: wild guess
                response = self.reload()
                content = response.read()
                continue
            m = _wait1_search(content)
            if m is None:
                break
            seconds = int(m.group(1)) * 60
            yield seconds
            response = self.reload()
            content = response.read()
        if _race_search(content):
            self.report_simultaneous_download()
        m = _uri_search(content)
        if m is None:
            self.report_api_error(code='uri')
        uri = m.group(1)
        m = _wait2_search(content)
        if m is None:
            self.report_api_error(code='wait')
        seconds = int(m.group(1))
        yield seconds
        self.wget(uri, target)

# vim:ts=4 sw=4 et

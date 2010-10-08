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
_captcha_search = re.compile(r'<img src="([^"]*/gencap.php[?][0-9a-f]+[.]gif)"').search
_wait_search = re.compile(r'^\s*count=(\d+);', re.MULTILINE).search
_uri_search = re.compile(r'id="downloadlink"><a href="(http://[a-z0-9]+[.]megaupload[.]com/files/[0-9a-f]+/([^"/]+))"').search;
	
del re

from leechy import Browser

class Browser(Browser):

    pattern = r'^http://(www[.])?megaupload[.]com(/[a-z]+)?/[?]d=[a-zA-Z0-9]+$'

    def enhance_captcha(self, image):
        try:
            import ImageEnhance
        except:
            return image
        enhancer = ImageEnhance.Contrast(image)
        return enhancer.enhance(100)

    def download(self):
        import os
        import urllib
        response = self.open(self.start_uri)
        content = response.read()
        captcha_match = _captcha_search(content)
        if captcha_match is None:
            self.report_api_error(code='c')
        while captcha_match is not None:
            captcha_uri = captcha_match.group(1)
            captcha_uri = urllib.basejoin(self.start_uri, captcha_uri)
            captcha = self.open_novisit(captcha_uri)
            token = self.read_captcha(captcha)
            self.select_form(nr=0)
            self['captcha'] = token
            response = self.submit()
            content = response.read()
            captcha_match = _captcha_search(content)
        m = _uri_search(content)
        if m is None:
            self.report_api_error(code='uri')
        target = m.group(2)
        uri = m.group(1)
        if os.path.exists(target):
            self.log_info('Nothing to do.')
            return
        m = _wait_search(content)
        if m is None:
            self.report_api_error(code='wait')
        seconds = int(m.group(1))
        yield seconds
        self.wget(uri, target)

# vim:ts=4 sw=4 et

# encoding=UTF-8

# Copyright © 2009 Jakub Wilk <ubanus@users.sf.net>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 dated June, 1991.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.

import re
_captcha_search = re.compile(r'<img src="([^"]*/gencap.php[?][0-9a-f]+)"').search
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
            self.api_error(code='c')
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
        vars = {}
        m = _uri_search(content)
        if m is None:
            self.api_error(code='uri')
        target = m.group(2)
        uri = m.group(1)
        if os.path.exists(target):
            self.log_info('Nothing to do.')
            return
        m = _wait_search(content)
        if m is None:
            self.api_error(code='wait')
        seconds = int(m.group(1))
        self.sleep(seconds)
        self.wget(uri, target)

# vim:ts=4 sw=4 et

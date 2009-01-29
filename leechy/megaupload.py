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
_captcha_search = re.compile(r'<img src="(/capgen.php[?][0-9a-f]+)">').search
_wait_search = re.compile(r'^\s*x\d+=(\d+);', re.MULTILINE).search
_code_v1_search = re.compile(r'^\s*var ([a-z]) = String[.]fromCharCode[(]Math[.]abs[(]-([0-9]+)[)][)];', re.MULTILINE).search;
_code_v2_search = re.compile(r"^\s*var ([a-z]) = '([0-9a-f])' [+] String[.]fromCharCode[(]Math[.]sqrt[(](\d+)[)][)];", re.MULTILINE).search;
_uri_search = re.compile(r'"(http://www\d+[.]megaupload[.]com/files/[0-9a-f]+)\' [+] ([a-z]) [+] ([a-z]) [+] \'([0-9a-f]+/)([^/"]+)"').search;
del re

from leechy import Browser

class Browser(Browser):

    pattern = r'^http://(www[.])?megaupload[.]com(/[a-z]+)?/[?]d=[A-Z0-9]+$'

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
            self['imagestring'] = token
            response = self.submit()
            content = response.read()
            captcha_match = _captcha_search(content)
        vars = {}
        v1 = _code_v1_search(content)
        if v1 is None:
            self.api_error(code='v1')
        v2 = _code_v2_search(content)
        if v2 is None:
            self.api_error(code='v2')
        vars[v1.group(1)] = chr(int(v1.group(2)))
        vars[v2.group(1)] = v2.group(2) + chr(int(int(v2.group(3)) ** 0.5))
        m = _uri_search(content)
        if m is None:
            self.api_error(code='uri')
        target = m.group(5)
        uri = m.group(1) + vars[m.group(2)] + vars[m.group(3)] + m.group(4) + target
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

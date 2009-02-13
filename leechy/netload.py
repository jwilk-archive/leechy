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
_target_search = re.compile('<div class="dl_first_filename">\s+([^<]+)').search
_click_link_re = re.compile('captcha=1')
_wait1_search = re.compile(r'<script type="text/javascript">countdown[(](\d+),').search
_captcha_search = re.compile('<img style="[^"]+" src="(share/includes/captcha.php[?]t=\d+)"').search
_uri_search = re.compile('<a class="Orange_Link" href="(http://[0-9.]+/[0-9a-f]+)"').search
del re

from leechy import Browser

class Browser(Browser):

    pattern = r'^http://netload[.]in/[0-9a-zA-Z]+/'

    def download(self):
        import urlparse
        import os
        response =self.open(self.start_uri)
        content = response.read()
        target_match = _target_search(content)
        if target_match is None:
            self.api_error('target')
        target = target_match.group(1)
        if os.path.exists(target):
            self.log_info('Nothing to do.')
            return
        response = self.follow_link(url_regex=_click_link_re)
        content = response.read()
        sleep_match = _wait1_search(content)
        if sleep_match is None:
            self.api_error('sleep1')
        seconds = (int(sleep_match.group(1)) + 99) // 100
        captcha_match = _captcha_search(content)
        if captcha_match is None:
            self.api_error()
        captcha_uri = '/' + captcha_match.group(1)
        captcha = self.open_novisit(captcha_uri)
        token = self.read_captcha(captcha)
        self.sleep(seconds)
        self.select_form(nr=0)
        self['captcha_check'] = token
        response = self.submit()
        content = response.read()
        if sleep_match is None:
            self.api_error('sleep2')
        seconds = (int(sleep_match.group(1)) + 99) // 100
        uri_match = _uri_search(content)
        if uri_match is None:
            self.api_error('uri')
        uri = uri_match.group(1)
        self.sleep(seconds)
        self.wget(uri, target)

# vim:ts=4 sw=4 et

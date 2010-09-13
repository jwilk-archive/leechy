# encoding=UTF-8

# Copyright © 2010 Jakub Wilk <jwilk@jwilk.net>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 dated June, 1991.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.

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

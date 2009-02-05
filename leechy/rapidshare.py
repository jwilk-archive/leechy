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
_wait1_search = re.compile(r'Or try again in about (\d+) minutes').search
_wait2_search = re.compile(r'^var c=(\d+);', re.MULTILINE).search
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
                self.file_not_found()
            else:
                self.api_error('noforms')
        self.select_form(nr=0);
        response = self.submit()
        content = response.read()
        while True:
            m = _wait1_search(content)
            if m is None:
                break
            seconds = int(m.group(1)) * 60
            self.sleep(seconds)
            response = self.reload()
            content = response.read()
        if _race_search(content):
            self.simultaneous_download()
        m = _uri_search(content)
        if m is None:
            self.api_error(code='uri')
        uri = m.group(1)
        m = _wait2_search(content)
        if m is None:
            self.api_error(code='wait')
        seconds = int(m.group(1))
        self.sleep(seconds)
        self.wget(uri, target)

# vim:ts=4 sw=4 et

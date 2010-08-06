# encoding=UTF-8

# Copyright © 2009 Jakub Wilk <jwilk@jwilk.net>
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
